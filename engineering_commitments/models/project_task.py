# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# =========================================================
# 1. SIGN TEMPLATE EXTENSION (Added Document Type & Package)
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


# =========================================================
# 2. SUPPORTING MODELS FOR COMPANY CONTRACTS & PHASES APPROVALS
# =========================================================
# --- COMMITMENTS (Added action_sign_now for direct sign) ---
class EngineeringProjectCommitment(models.Model):
    _name = 'engineering.project.commitment'
    _description = 'Engineering Project Commitment Line'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if self.sign_request_id:
            return self.sign_request_id.go_to_document()

class EngineeringTaskCommitment(models.Model):
    _name = 'engineering.task.commitment'
    _description = 'Engineering Task Commitment Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if self.sign_request_id:
            return self.sign_request_id.go_to_document()


# --- COMPANY CONTRACTS ---
class EngineeringProjectCompanyContract(models.Model):
    _name = 'engineering.project.company.contract'
    _description = 'Engineering Project Company Contract Line'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if self.sign_request_id:
            return self.sign_request_id.go_to_document()


class EngineeringTaskCompanyContract(models.Model):
    _name = 'engineering.task.company.contract'
    _description = 'Engineering Task Company Contract Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if self.sign_request_id:
            return self.sign_request_id.go_to_document()


# --- PHASES APPROVAL ---
class EngineeringProjectPhaseApproval(models.Model):
    _name = 'engineering.project.phase.approval'
    _description = 'Engineering Project Phase Approval Line'

    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if self.sign_request_id:
            return self.sign_request_id.go_to_document()


class EngineeringTaskPhaseApproval(models.Model):
    _name = 'engineering.task.phase.approval'
    _description = 'Engineering Task Phase Approval Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if self.sign_request_id:
            return self.sign_request_id.go_to_document()


# =========================================================
# 3. PROJECT.PROJECT MODEL
# =========================================================
class ProjectProject(models.Model):
    _inherit = 'project.project'

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
        """ Helper method to build the exact search domain for templates """
        domain = [('document_type', '=', doc_type)]

        # 1. Building Type
        building_type = getattr(self, 'building_type', False)
        if building_type:
            domain.append(('building_type', 'in', [building_type, 'all']))
        else:
            domain.append(('building_type', '=', 'all'))

        # 2. Service Type
        service_type = getattr(self, 'service_type', False)
        if service_type:
            domain.append(('service_type', 'in', [service_type, 'all']))
        else:
            domain.append(('service_type', '=', 'all'))

        # 3. Package Check (Fetches securely from Sale Order if missing on project)
        pack = getattr(self, 'engineering_package_id', False)
        if not pack and getattr(self, 'sale_order_id', False):
            pack = getattr(self.sale_order_id, 'engineering_package_id', False)

        if pack:
            domain.extend(['|', ('package_id', '=', False), ('package_id', '=', pack.id)])
        else:
            domain.append(('package_id', '=', False))

        return domain

    # ---------------------------------------------------------
    # COMMITMENTS FUNCTIONS
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
        required_commitments = self.commitment_ids.filtered(lambda c: c.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as Required."))

        self._generate_pdfs_for_lines(required_commitments)
        return True

    # ---------------------------------------------------------
    # COMPANY CONTRACTS FUNCTIONS
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
        required_contracts = self.company_contract_ids.filtered(lambda c: c.is_required)
        if not required_contracts:
            raise UserError(_("Please mark at least one company contract as Required."))

        self._generate_pdfs_for_lines(required_contracts)
        return True

    # ---------------------------------------------------------
    # PHASES APPROVAL FUNCTIONS
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
        required_approvals = self.phase_approval_ids.filtered(lambda c: c.is_required)
        if not required_approvals:
            raise UserError(_("Please mark at least one phases approval as Required."))

        self._generate_pdfs_for_lines(required_approvals)
        return True


    # ---------------------------------------------------------
    # HELPER FUNCTION FOR ALL
    # ---------------------------------------------------------
    def _generate_pdfs_for_lines(self, lines):
        project = self
        if not project.partner_id:
            raise UserError(_("Project must have a customer."))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        current_partner = self.env.user.partner_id

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
            
            project_area = getattr(project, 'area', False)
            raw_gov_name = project.governorate_id.name if getattr(project, 'governorate_id', False) else ''
            clean_gov_name = raw_gov_name.replace('محافظة', '').replace('محافظه', '').strip()

            replacements = {
                'name': f"          {project.partner_id.name or ''}",
                'date': fields.Date.context_today(self).strftime("%Y%m%d"),
                'governorate': f"          {clean_gov_name}",
                'region': f"          {project.region_id.name if getattr(project, 'region_id', False) else ''}",
                'block': f"          {getattr(project, 'block_no', '')}",
                'plot': f"          {getattr(project, 'plot_no', '')}",
                'area': str(project_area) if project_area else '', 
                'customer signature text': project.partner_id.name or '',
                'company signature text': self.env.company.name or '',
            }

            for item in template.sign_item_ids:
                field_name = (item.name or '').strip().lower()
                if field_name in replacements:
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

    # ---------------------------------------------------------
    # COMMITMENTS FUNCTIONS
    # ---------------------------------------------------------
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
        required_commitments = self.commitment_ids.filtered(lambda c: c.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as Required."))

        self._generate_pdfs_for_lines(required_commitments)
        return True

    # ---------------------------------------------------------
    # COMPANY CONTRACTS FUNCTIONS
    # ---------------------------------------------------------
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
        required_contracts = self.company_contract_ids.filtered(lambda c: c.is_required)
        if not required_contracts:
            raise UserError(_("Please mark at least one company contract as Required."))

        self._generate_pdfs_for_lines(required_contracts)
        return True

    # ---------------------------------------------------------
    # PHASES APPROVAL FUNCTIONS
    # ---------------------------------------------------------
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
        required_approvals = self.phase_approval_ids.filtered(lambda c: c.is_required)
        if not required_approvals:
            raise UserError(_("Please mark at least one phases approval as Required."))

        self._generate_pdfs_for_lines(required_approvals)
        return True


    # ---------------------------------------------------------
    # HELPER FUNCTION FOR ALL
    # ---------------------------------------------------------
    def _generate_pdfs_for_lines(self, lines):
        project = self.project_id
        if not project.partner_id:
            raise UserError(_("Project must have a customer."))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        current_partner = self.env.user.partner_id

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

            project_area = getattr(project, 'area', False)
            raw_gov_name = project.governorate_id.name if getattr(project, 'governorate_id', False) else ''
            clean_gov_name = raw_gov_name.replace('محافظة', '').replace('محافظه', '').strip()

            replacements = {
                'name': f"          {project.partner_id.name or ''}",
                'date': fields.Date.context_today(self).strftime("%Y%m%d"),
                'governorate': f"          {clean_gov_name}",
                'region': f"          {project.region_id.name if getattr(project, 'region_id', False) else ''}",
                'block': f"          {getattr(project, 'block_no', '')}",
                'plot': f"          {getattr(project, 'plot_no', '')}",
                'area': str(project_area) if project_area else '', 
                'customer signature text': project.partner_id.name or '',
                'company signature text': self.env.company.name or '',
            }

            for item in template.sign_item_ids:
                field_name = (item.name or '').strip().lower()
                _logger.warning(f"FIELD DETECTED >>> '{field_name}'")
                if field_name in replacements:
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

    def action_quick_sign_phase(self):
        """ Quick action from the tree view to generate and immediately jump to signing """
        self.ensure_one()
        
        # 1. Load the phase template if it isn't loaded yet
        if not self.phase_approval_ids:
            self.action_load_phases_approvals()
        
        # 2. Force mark at least the first template as "Required" automatically
        if self.phase_approval_ids and not self.phase_approval_ids.filtered(lambda p: p.is_required):
            self.phase_approval_ids[0].is_required = True
            
        # 3. Generate the PDF signature document
        unsigned = self.phase_approval_ids.filtered(lambda p: p.is_required and not p.sign_request_id)
        if unsigned:
            self._generate_pdfs_for_lines(unsigned)
            
        # 4. Jump straight into the Signing page window directly!
        sign_request = self.phase_approval_ids.filtered(lambda p: p.sign_request_id).mapped('sign_request_id')
        if sign_request:
            # THIS is the magic line that redirects you straight to the signing canvas
            return sign_request[0].go_to_document()