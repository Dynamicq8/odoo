# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# =========================================================
# PROJECT.PROJECT MODEL
# =========================================================
class ProjectProject(models.Model):
    _inherit = 'project.project'

    commitment_ids = fields.One2many(
        'engineering.project.commitment', 
        'project_id',
        string='Engineering Commitments (التعهدات)'
    )

    def action_load_commitments(self):
        for project in self:
            # Base domain for commitments
            domain = [('is_commitment', '=', True)]

            # 1. Check Building Type
            building_type = getattr(project, 'building_type', False)
            if building_type:
                domain.append(('building_type', 'in', [building_type, 'all']))
            else:
                domain.append(('building_type', '=', 'all'))

            # 2. Check Service Type
            service_type = getattr(project, 'service_type', False)
            if service_type:
                domain.append(('service_type', 'in', [service_type, 'all']))
            else:
                domain.append(('service_type', '=', 'all'))

            # Search templates matching BOTH conditions
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

        project = self
        if not project.partner_id:
            raise UserError(_("Project must have a customer."))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        current_partner = self.env.user.partner_id

        for commitment in required_commitments:
            if commitment.sign_request_id and commitment.sign_request_id.state == 'signed':
                continue
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                commitment.sign_request_id.cancel()
                commitment.sign_request_id = False

            template = commitment.sign_template_id
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
            
            replacements = {
                'name': project.partner_id.name or '',
                'date': fields.Date.context_today(self).strftime("%Y/%m/%d"),
                'governorate': project.governorate_id.name if getattr(project, 'governorate_id', False) else '',
                'region': project.region_id.name if getattr(project, 'region_id', False) else '',
                'block': getattr(project, 'block_no', ''),
                'plot': getattr(project, 'plot_no', ''),
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

            commitment.sign_request_id = sign_request.id

        return True


# =========================================================
# PROJECT.TASK MODEL
# =========================================================
class ProjectTask(models.Model):
    _inherit = 'project.task'

    commitment_ids = fields.One2many(
        'engineering.task.commitment',
        'task_id',
        string='Engineering Commitments (التعهدات)'
    )

    def action_load_commitments(self):
        for task in self:
            project = task.project_id
            
            # Base domain for commitments
            domain = [('is_commitment', '=', True)]

            # 1. Check Building Type
            building_type = getattr(project, 'building_type', False)
            if building_type:
                domain.append(('building_type', 'in', [building_type, 'all']))
            else:
                domain.append(('building_type', '=', 'all'))

            # 2. Check Service Type
            service_type = getattr(project, 'service_type', False)
            if service_type:
                domain.append(('service_type', 'in', [service_type, 'all']))
            else:
                domain.append(('service_type', '=', 'all'))

            # Search templates matching BOTH conditions
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

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("Project must have a customer."))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        current_partner = self.env.user.partner_id

        for commitment in required_commitments:
            if commitment.sign_request_id and commitment.sign_request_id.state == 'signed':
                continue
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                commitment.sign_request_id.cancel()
                commitment.sign_request_id = False

            template = commitment.sign_template_id
            roles = list(set(template.sign_item_ids.mapped('responsible_id')))
            signers = []

            for role in roles:
                partner = project.partner_id if (role_customer and role.id == role_customer.id) else current_partner
                signers.append((0, 0, {'role_id': role.id, 'partner_id': partner.id,}))

            if not signers:
                raise UserError(_("Template has no signers."))

            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {self.name}",
                'request_item_ids': signers,
            })

            replacements = {
                'name': project.partner_id.name or '',
                'date': fields.Date.context_today(self).strftime("%Y/%m/%d"),
                'governorate': project.governorate_id.name if getattr(project, 'governorate_id', False) else '',
                'region': project.region_id.name if getattr(project, 'region_id', False) else '',
                'block': getattr(project, 'block_no', ''),
                'plot': getattr(project, 'plot_no', ''),
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
            commitment.sign_request_id = sign_request.id
        return True