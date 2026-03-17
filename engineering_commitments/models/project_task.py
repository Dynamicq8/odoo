# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, _, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    commitment_ids = fields.One2many(
        'engineering.task.commitment', 
        'task_id', 
        string='Engineering Commitments (التعهدات)'
    )

    def action_load_commitments(self):
        for task in self:
            building_type = getattr(task.project_id, 'building_type', False)
            if not building_type:
                domain = [('is_commitment', '=', True), ('building_type', '=', 'all')]
            else:
                domain = [('is_commitment', '=', True), ('building_type', 'in', [building_type, 'all'])]
            
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

        required_commitments = self.commitment_ids.filtered(lambda p: p.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as 'Required' first."))

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("The project must have a Customer to generate documents."))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)

        # ==========================================
        # 1. GET VALUES FROM PROJECT (with debug fallbacks)
        # ==========================================
        replacements = {
            'Name': project.partner_id.name or "NO NAME",
            'Date': fields.Date.context_today(self).strftime("%Y/%m/%d"),
            'Governorate': project.governorate_id.name if project.governorate_id else "NO GOV",
            'Region': project.region_id.name if project.region_id else "NO REGION",
            'Block': project.block_no or "NO BLOCK",
            'Plot': project.plot_no or "NO PLOT",
        }

        generated_requests = self.env['sign.request']

        for commitment in required_commitments:
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                generated_requests |= commitment.sign_request_id
                continue

            template = commitment.sign_template_id
            if not template.sign_item_ids:
                raise UserError(_(f"Template '{template.name}' has no fields configured."))

            # 2. Define the Signers
            roles = template.sign_item_ids.mapped('responsible_id')
            signers_list = []
            for role in roles:
                partner_id = project.partner_id.id if (role_customer and role.id == role_customer.id) else self.env.user.partner_id.id
                signers_list.append({'role_id': role.id, 'partner_id': partner_id})

            # ==========================================
            # 3. CREATE THE REQUEST AND THEN FILL IT
            # This is the most compatible way.
            # ==========================================
            sign_request = template.with_context(
                sign_directly_without_mail=True
            ).create_request(
                {'request_item_ids': [(0, 0, s) for s in signers_list]},
                without_mail=True
            )

            # 4. Loop through the created signers and fill in their fields
            for signer in sign_request.request_item_ids:
                for field in template.sign_item_ids:
                    # Match the signer's role to the field's role
                    if signer.role_id.id == field.responsible_id.id:
                        field_name = field.name
                        if field_name in replacements:
                            value_to_insert = replacements[field_name]
                            
                            # Find the specific input box for this signer and this field
                            item_value = sign_request.request_item_value_ids.filtered(
                                lambda v: v.sign_item_id.id == field.id and v.sign_request_item_id.id == signer.id
                            )
                            if item_value:
                                item_value.write({'value': value_to_insert})

            commitment.sign_request_id = sign_request.id
            generated_requests |= sign_request

        if not generated_requests:
            return True

        # 5. Open the document(s)
        action = self.env['ir.actions.actions']._for_xml_id('sign.sign_request_action')
        if len(generated_requests) == 1:
            action.update({'view_mode': 'form', 'res_id': generated_requests.id, 'views': [(False, 'form')]})
        else:
            action['domain'] = [('id', 'in', generated_requests.ids)]
        
        return action
