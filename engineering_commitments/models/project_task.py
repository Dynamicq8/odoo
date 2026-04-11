# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import re
import urllib.parse
import json # <--- ADDED THIS LINE HERE

_logger = logging.getLogger(__name__)


# =========================================================
# 1. SIGN TEMPLATE EXTENSION
# =========================================================
class SignTemplate(models.Model):
    _inherit = 'sign.template'

    document_type = fields.Selection([
        ('commitment', 'تعهد هندسي (Engineering Commitment)'),
        ('company_contract', 'عقد شركة (Company Contract)'),
        ('phases_approval', 'اعتماد المراحل (Phases Approval)'),
        ('none', 'غير محدد (None)')
    ], string="Document Type (نوع المستند)", default='none',
       help="Choose whether this is an Engineering Commitment, Company Contract, or Phases Approval.")

    package_id = fields.Many2one('engineering.package', string="الباقة (Package)",
        help="If selected, this contract will only load for projects using this package.")

    building_type = fields.Selection([
        ('residential', 'سكن خاص'),
        ('investment', 'استثماري'),
        ('commercial', 'تجاري'),
        ('industrial', 'صناعي'),
        ('cooperative', 'جمعيات وتعاونيات'),
        ('mosque', 'مساجد'),
        ('hangar', 'مخازن / شبرات'),
        ('farm', 'مزارع'),
        ('all', 'جميع الأنواع')
    ], string="Building Type (نوع العقار)", default='all')

    service_type = fields.Selection([
        ('new_construction', 'بناء جديد'),
        ('demolition', 'هدم'),
        ('modification', 'تعديل'),
        ('addition', 'اضافة'),
        ('addition_modification', 'تعديل واضافة'),
        ('supervision_only', 'إشراف هندسي فقط'),
        ('renovation', 'ترميم'),
        ('internal_partitions', 'قواطع داخلية'),
        ('shades_garden', 'مظلات / حدائق'),
        ('all', 'جميع الأنواع')
    ], string="Service Type (نوع الخدمة)", default='all')


# Refactored direct actions to be more flexible
def _action_sign_now_direct(self_record): # Changed self to self_record to avoid conflict with class self
    self_record.ensure_one()
    if not self_record.sign_request_id:
        raise UserError(_("No generated document yet."))

    request = self_record.sign_request_id
    user = self_record.env.user

    request_item = request.request_item_ids.filtered(
        lambda r: r.partner_id.id == user.partner_id.id
    )
    if not request_item:
        request_item = request.request_item_ids[:1] # Fallback to first if user not found
    if not request_item:
        raise UserError(_("You are not assigned to sign this document, and no other signers were found."))

    return {
        'type': 'ir.actions.act_url',
        'url': f'/sign/document/{request.id}/{request_item[0].access_token}',
        'target': 'new',
    }


def _action_send_whatsapp_direct(self_record): # Changed self to self_record
    """
    Build a WhatsApp URL containing the signing link and open it in a new tab.
    The phone number is read from the customer (partner_id) on the linked
    project or task. Falls back to the current user's partner phone if the
    customer has no mobile/phone set.

    Priority for phone: partner.mobile → partner.phone → current user mobile/phone
    """
    self_record.ensure_one()
    if not self_record.sign_request_id:
        raise UserError(_("لا يوجد مستند محدد بعد. يرجى توليد PDF أولاً.\n(No document generated yet. Please generate the PDF first.)"))

    request = self_record.sign_request_id

    # ------------------------------------------------------------------ #
    # 1. Resolve the customer partner from project_id or task_id
    # ------------------------------------------------------------------ #
    partner = None

    if hasattr(self_record, 'project_id') and self_record.project_id:
        partner = self_record.project_id.partner_id
    elif hasattr(self_record, 'task_id') and self_record.task_id:
        partner = self_record.task_id.project_id.partner_id

    if not partner:
        partner = self_record.env.user.partner_id

    # ------------------------------------------------------------------ #
    # 2. Get phone number (mobile preferred over phone)
    # ------------------------------------------------------------------ #
    phone = (partner.mobile or partner.phone or '').strip()

    if not phone:
        # Last resort: current user
        phone = (self_record.env.user.partner_id.mobile or self_record.env.user.partner_id.phone or '').strip()

    if not phone:
        raise UserError(_(
            "لا يوجد رقم هاتف مسجل للعميل.\n"
            "Please set a mobile/phone number on the customer record before sending via WhatsApp."
        ))

    # ------------------------------------------------------------------ #
    # 3. Normalise phone to international format
    #    Strips spaces, dashes, parentheses.
    #    If number starts with 0, replace leading 0 with country code 965
    #    (Kuwait default – adjust as needed).
    # ------------------------------------------------------------------ #
    
    phone_clean = re.sub(r'[\s\-\(\)]+', '', phone)
    if phone_clean.startswith('00'):
        phone_clean = '+' + phone_clean[2:]
    elif phone_clean.startswith('0'):
        phone_clean = '965' + phone_clean[1:]      # ← change 965 to your country code if needed
    phone_clean = phone_clean.lstrip('+')           # wa.me does not want the leading +

    # ------------------------------------------------------------------ #
    # 4. Build the signing URL (Includes access_token so no login needed)
    # ------------------------------------------------------------------ #
    request_item = request.request_item_ids.filtered(
        lambda r: r.partner_id.id == partner.id
    )
    if not request_item:
        request_item = request.request_item_ids[:1]

    if not request_item:
        raise UserError(_("No signer found on this sign request."))

    base_url = self_record.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
    sign_url = f"{base_url}/sign/document/{request.id}/{request_item[0].access_token}"

    # ------------------------------------------------------------------ #
    # 5. Compose WhatsApp message
    # ------------------------------------------------------------------ #
    doc_name = request.reference or self_record.sign_template_id.name or _("المستند")
    message = (
        f"مرحباً {partner.name}،\n\n"
        f"يرجى مراجعة وتوقيع المستند التالي:\n"
        f"📄 {doc_name}\n\n"
        f"🔗 رابط التوقيع:\n{sign_url}\n\n"
        f"شكراً لتعاملكم معنا."
    )

    whatsapp_url = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(message)}"

    return {
        'type': 'ir.actions.act_url',
        'url': whatsapp_url,
        'target': 'new',
    }


# =========================================================
# 2. SUPPORTING MODELS
# =========================================================
class EngineeringProjectCommitment(models.Model):
    _name = 'engineering.project.commitment'
    _description = 'Engineering Project Commitment Line'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        return _action_sign_now_direct(self)

    # ADDED WhatsApp feature
    def action_send_whatsapp(self):
        return _action_send_whatsapp_direct(self)


class EngineeringTaskCommitment(models.Model):
    _name = 'engineering.task.commitment'
    _description = 'Engineering Task Commitment Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        return _action_sign_now_direct(self)
        
    # ADDED WhatsApp feature
    def action_send_whatsapp(self):
        return _action_send_whatsapp_direct(self)


class EngineeringProjectCompanyContract(models.Model):
    _name = 'engineering.project.company.contract'
    _description = 'Engineering Project Company Contract Line'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        return _action_sign_now_direct(self)

    def action_send_whatsapp(self):
        return _action_send_whatsapp_direct(self)


class EngineeringTaskCompanyContract(models.Model):
    _name = 'engineering.task.company.contract'
    _description = 'Engineering Task Company Contract Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        return _action_sign_now_direct(self)

    def action_send_whatsapp(self):
        return _action_send_whatsapp_direct(self)


class EngineeringProjectPhaseApproval(models.Model):
    _name = 'engineering.project.phase.approval'
    _description = 'Engineering Project Phase Approval Line'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        return _action_sign_now_direct(self)


class EngineeringTaskPhaseApproval(models.Model):
    _name = 'engineering.task.phase.approval'
    _description = 'Engineering Task Phase Approval Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        return _action_sign_now_direct(self)


# =========================================================
# 3. PROJECT.PROJECT MODEL
# =========================================================
class ProjectProject(models.Model):
    _inherit = 'project.project'

    # -------------------------------------------------------
    # DO NOT redefine building_type or service_type here.
    # They are already defined as stored Selection fields
    # in engineering_quotation. Redefining them causes a
    # silent field conflict that breaks domain filtering.
    #
    # ONLY add engineering_package_id — it is missing from
    # engineering_quotation's project.project definition.
    # -------------------------------------------------------
    engineering_package_id = fields.Many2one(
        'engineering.package',
        string="الباقة (Package)",
        store=True,
    )

    commitment_ids = fields.One2many(
        'engineering.project.commitment',
        'project_id',
        string='Engineering Commitments (التعهدات)'
    )

    company_contract_ids = fields.One2many(
        'engineering.project.company.contract',
        'project_id',
        string='Company Contracts (عقود الشركة)'
    )

    phase_approval_ids = fields.One2many(
        'engineering.project.phase.approval',
        'project_id',
        string='Phases Approvals (اعتماد المراحل)'
    )

    def _get_sign_template_domain(self, doc_type):
        """
        Build domain for sign templates using building_type, service_type,
        and engineering_package_id stored directly on the project.
        Falls back to sale_order_id if values are missing on the project.
        """
        domain = [('document_type', '=', doc_type)]

        # Read from project directly (set at project creation from sale order)
        building_type = self.building_type or False
        service_type = self.service_type or False
        pack = self.engineering_package_id or False

        # Fallback to sale order in case project was created without these values
        if not building_type and self.sale_order_id:
            building_type = self.sale_order_id.building_type
        if not service_type and self.sale_order_id:
            service_type = self.sale_order_id.service_type
        if not pack and self.sale_order_id:
            pack = getattr(self.sale_order_id, 'engineering_package_id', False)

        # 1. Building Type filter (CRITICAL FIX: Included 'False' for older/unset templates)
        if building_type:
            domain.append(('building_type', 'in', [building_type, 'all', False]))
        else:
            domain.append(('building_type', 'in', ['all', False]))

        # 2. Service Type filter (CRITICAL FIX: Included 'False' for older/unset templates)
        if service_type:
            domain.append(('service_type', 'in', [service_type, 'all', False]))
        else:
            domain.append(('service_type', 'in', ['all', False]))

        # 3. Package filter
        if pack:
            domain.extend(['|', ('package_id', '=', False), ('package_id', '=', pack.id)])
        else:
            domain.append(('package_id', '=', False))

        _logger.warning(
            f"_get_sign_template_domain >>> doc_type={doc_type} | "
            f"building_type={building_type} | service_type={service_type} | "
            f"pack={pack} | domain={domain}"
        )

        return domain

    # ---------------------------------------------------------
    # COMMITMENTS
    # ---------------------------------------------------------
    def action_load_commitments(self):
        for project in self:
            domain = project._get_sign_template_domain('commitment')
            templates = self.env['sign.template'].search(domain)
            existing_template_ids = project.commitment_ids.mapped('sign_template_id.id')
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.project.commitment'].create({
                        'project_id': project.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_commitments_pdf(self):
        self.ensure_one()
        required = self.commitment_ids.filtered(lambda c: c.is_required)
        if not required:
            raise UserError(_("Please mark at least one commitment as Required."))
        self._generate_pdfs_for_lines(required)
        return True

    # ---------------------------------------------------------
    # COMPANY CONTRACTS
    # ---------------------------------------------------------
    def action_load_company_contracts(self):
        for project in self:
            domain = project._get_sign_template_domain('company_contract')
            templates = self.env['sign.template'].search(domain)
            existing_template_ids = project.company_contract_ids.mapped('sign_template_id.id')
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.project.company.contract'].create({
                        'project_id': project.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_company_contracts_pdf(self):
        self.ensure_one()
        required = self.company_contract_ids.filtered(lambda c: c.is_required)
        if not required:
            raise UserError(_("Please mark at least one company contract as Required."))
        self._generate_pdfs_for_lines(required)
        return True

    # ---------------------------------------------------------
    # PHASES APPROVALS
    # ---------------------------------------------------------
    def action_load_phases_approvals(self):
        for project in self:
            domain = project._get_sign_template_domain('phases_approval')
            templates = self.env['sign.template'].search(domain)
            existing_template_ids = project.phase_approval_ids.mapped('sign_template_id.id')
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.project.phase.approval'].create({
                        'project_id': project.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_phases_approvals_pdf(self):
        self.ensure_one()
        required = self.phase_approval_ids.filtered(lambda c: c.is_required)
        if not required:
            raise UserError(_("Please mark at least one phases approval as Required."))
        self._generate_pdfs_for_lines(required)
        return True

    # ---------------------------------------------------------
    # SHARED PDF GENERATOR - MODIFIED TO INCLUDE SEAL IMAGE
    # ---------------------------------------------------------
    def _generate_pdfs_for_lines(self, lines):
        project = self
        if not project.partner_id:
            raise UserError(_("Project must have a customer."))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        current_partner = self.env.user.partner_id
        company = self.env.company # Get the current company record

        # Get the company seal image (base64) if available
        company_seal_b64 = company.company_seal_image if company.company_seal_image else False
        company_seal_filename = company.company_seal_filename or "seal.png"

        for line in lines:
            if line.sign_request_id and line.sign_request_id.state == 'signed':
                continue
            if line.sign_request_id and line.sign_request_id.state != 'canceled':
                line.sign_request_id.cancel()
                line.sign_request_id = False

            template = line.sign_template_id
            roles = list(set(template.sign_item_ids.mapped('responsible_id')))
            signers = []

            for role in roles:
                partner = project.partner_id if (role_customer and role.id == role_customer.id) else current_partner
                signers.append((0, 0, {'role_id': role.id, 'partner_id': partner.id}))

            if not signers:
                raise UserError(_("Template has no signers."))

            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {self.name}",
                'request_item_ids': signers,
            })

            raw_gov_name = project.governorate_id.name if getattr(project, 'governorate_id', False) else ''
            clean_gov_name = raw_gov_name.replace('محافظة', '').replace('محافظه', '').strip()

            # --- التعديل لترجمة اليوم من الإنجليزية إلى العربية ---
            current_date = fields.Date.context_today(self)
            arabic_days = {
                0: 'الإثنين',
                1: 'الثلاثاء',
                2: 'الأربعاء',
                3: 'الخميس',
                4: 'الجمعة',
                5: 'السبت',
                6: 'الأحد'
            }
            arabic_day_str = arabic_days.get(current_date.weekday(), '')

            # --- القاموس المحدث ---
            replacements = {
                'name': f"          {project.partner_id.name or ''}",
                'date': current_date.strftime("%d/%m/%Y"),
                'day': f"          {arabic_day_str}", # <==== إضافة اليوم بالعربية
                'nationality': f"          كويتي",      # <==== إضافة الجنسية ثابتة "كويتي"
                'governorate': f"          {clean_gov_name}",
                'region': f"          {project.region_id.name if getattr(project, 'region_id', False) else ''}",
                'block': f"          {getattr(project, 'block_no', '')}",
                'plot': f"          {getattr(project, 'plot_no', '')}",
                'area': str(getattr(project, 'area', '') or ''),
                'civil': f"          {getattr(project, 'civil_number', '')}",
                'customer signature text': project.partner_id.name or '',
                'company signature text': self.env.company.name or '',
            }

            for item in template.sign_item_ids:
                field_name = (item.name or '').strip().lower()
                _logger.warning(f"FIELD DETECTED >>> '{field_name}'")

                # --- NEW LOGIC FOR FILLING 'SEAL' FIELD WITH IMAGE ---
               if field_name == 'seal' and company_seal_b64:
                # Odoo Sign image fields expect a plain base64 data URL, not a JSON object.
                # company.company_seal_image is stored as base64-encoded bytes (Binary field).
                # We decode the bytes to a plain string, then build a data URL.
                if isinstance(company_seal_b64, bytes):
                    seal_b64_str = company_seal_b64.decode('utf-8')
                else:
                    seal_b64_str = company_seal_b64  # already a string

                # Detect MIME type from filename, default to png
                fname = (company.company_seal_filename or 'seal.png').lower()
                if fname.endswith('.jpg') or fname.endswith('.jpeg'):
                    mime = 'image/jpeg'
                elif fname.endswith('.gif'):
                    mime = 'image/gif'
                else:
                    mime = 'image/png'

                value_to_store = f"data:{mime};base64,{seal_b64_str}"

                _logger.warning(
                    f"FILLING SEAL FIELD with IMAGE data URL (first 80 chars): "
                    f"{value_to_store[:80]}..."
                )

                signer = sign_request.request_item_ids.filtered(
                    lambda r: r.role_id.id == item.responsible_id.id
                )
                if signer:
                    self.env['sign.request.item.value'].sudo().create({
                        'sign_request_id': sign_request.id,
                        'sign_request_item_id': signer[0].id,
                        'sign_item_id': item.id,
                        'value': value_to_store,
                    })

                elif field_name in replacements:
                    value = replacements[field_name]
                    signer = sign_request.request_item_ids.filtered(
                        lambda r: r.role_id.id == item.responsible_id.id
                    )
                    if signer:
                        self.env['sign.request.item.value'].sudo().create({
                            'sign_request_id': sign_request.id,
                            'sign_request_item_id': signer[0].id,
                            'sign_item_id': item.id,
                            'value': value,
                        })

            line.sign_request_id = sign_request.id


# =========================================================
# 4. PROJECT.TASK MODEL
# =========================================================
class ProjectTask(models.Model):
    _inherit = 'project.task'

    parent_task_name = fields.Char(
        string="Parent Task Name",
        related='parent_id.name',
        store=True,
        readonly=True
    )

    commitment_ids = fields.One2many(
        'engineering.task.commitment',
        'task_id',
        string='Engineering Commitments (التعهدات)'
    )

    company_contract_ids = fields.One2many(
        'engineering.task.company.contract',
        'task_id',
        string='Company Contracts (عقود الشركة)'
    )

    phase_approval_ids = fields.One2many(
        'engineering.task.phase.approval',
        'task_id',
        string='Phases Approvals (اعتماد المراحل)'
    )

    def action_load_commitments(self):
        for task in self:
            domain = task.project_id._get_sign_template_domain('commitment')
            templates = self.env['sign.template'].search(domain)
            existing_template_ids = task.commitment_ids.mapped('sign_template_id.id')
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.task.commitment'].create({
                        'task_id': task.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_commitments_pdf(self):
        self.ensure_one()
        required = self.commitment_ids.filtered(lambda c: c.is_required)
        if not required:
            raise UserError(_("Please mark at least one commitment as Required."))
        self._generate_pdfs_for_lines(required)
        return True

    def action_load_company_contracts(self):
        for task in self:
            domain = task.project_id._get_sign_template_domain('company_contract')
            templates = self.env['sign.template'].search(domain)
            existing_template_ids = task.company_contract_ids.mapped('sign_template_id.id')
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.task.company.contract'].create({
                        'task_id': task.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_company_contracts_pdf(self):
        self.ensure_one()
        required = self.company_contract_ids.filtered(lambda c: c.is_required)
        if not required:
            raise UserError(_("Please mark at least one company contract as Required."))
        self._generate_pdfs_for_lines(required)
        return True

    def action_load_phases_approvals(self):
        for task in self:
            domain = task.project_id._get_sign_template_domain('phases_approval')
            templates = self.env['sign.template'].search(domain)
            existing_template_ids = task.phase_approval_ids.mapped('sign_template_id.id')
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.task.phase.approval'].create({
                        'task_id': task.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_phases_approvals_pdf(self):
        self.ensure_one()
        required = self.phase_approval_ids.filtered(lambda c: c.is_required)
        if not required:
            raise UserError(_("Please mark at least one phases approval as Required."))
        self._generate_pdfs_for_lines(required)
        return True

    def _generate_pdfs_for_lines(self, lines):
        # We need to explicitly pass 'self' (the task record) to the project's method
        # if the project's method relies on project-specific context.
        # However, if the project method already gets the project from the lines,
        # we can keep it as is. For safety, let's adapt it to use the project
        # associated with the task for consistency.
        if self.project_id:
            self.project_id._generate_pdfs_for_lines(lines)
        else:
            raise UserError(_("Task must be linked to a Project to generate PDFs."))

    def action_quick_sign_phase(self):
        self.ensure_one()
        if not self.phase_approval_ids:
            self.action_load_phases_approvals()

        if self.phase_approval_ids and not self.phase_approval_ids.filtered('is_required'):
            self.phase_approval_ids[0].is_required = True

        unsigned = self.phase_approval_ids.filtered(lambda p: p.is_required and not p.sign_request_id)
        if unsigned:
            self._generate_pdfs_for_lines(unsigned)

        sign_line = self.phase_approval_ids.filtered(lambda p: p.is_required and p.sign_request_id)
        if sign_line:
            return sign_line[0].action_sign_now()