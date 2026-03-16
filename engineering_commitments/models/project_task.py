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
        """ Loads Sign templates based on the project's building type """
        for task in self:
            building_type = task.project_id.building_type if hasattr(task.project_id, 'building_type') else False
            
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
        """ Generates Sign Requests by mapping Roles to Partners and Autofilling values """
        self.ensure_one()

        required_commitments = self.commitment_ids.filtered(lambda p: p.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as 'Required' first. (يرجى تحديد تعهد واحد على الأقل كمطلوب)"))

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("The project must have a Customer to generate documents. (يجب تحديد عميل للمشروع)"))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        if not role_customer:
            raise UserError(_("Error: The 'Customer' role could not be found in the Sign application."))

        # --- AUTOFILL DICTIONARY ---
        replacements = {
            'Name': project.partner_id.name or "",
            'Date': fields.Date.context_today(self).strftime("%Y/%m/%d"),
            'Governorate': project.governorate_id.name if hasattr(project, 'governorate_id') and project.governorate_id else "",
            'Region': project.region_id.name if hasattr(project, 'region_id') and project.region_id else "",
            'Block': project.block_no or "" if hasattr(project, 'block_no') else "",
            'Plot': project.plot_no or "" if hasattr(project, 'plot_no') else "",
            'Street': project.street_no or "" if hasattr(project, 'street_no') else "",
        }

        generated_requests = self.env['sign.request']

        for commitment in required_commitments:
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                generated_requests |= commitment.sign_request_id
                continue

            template = commitment.sign_template_id
            if not template.sign_item_ids:
                raise UserError(_(f"Template '{template.name}' has no fields/signature configured."))

            # =========================================================
            # STEP 1: DEFINE THE SIGNERS (request_item_ids)
            # Find all unique roles on this template and assign partners
            # =========================================================
            roles = template.sign_item_ids.mapped('responsible_id')
            signers_list = []
            
            for role in roles:
                # If it's the customer role, use project customer. Otherwise, default to current user.
                partner_id = project.partner_id.id if role.id == role_customer.id else self.env.user.partner_id.id
                
                signers_list.append((0, 0, {
                    'role_id': role.id,
                    'partner_id': partner_id,
                }))

            # =========================================================
            # STEP 2: CREATE THE REQUEST
            # =========================================================
            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {project.name}",
                'request_item_ids': signers_list, # Passing SIGNERS, not box coordinates
            })

            # =========================================================
            # STEP 3: AUTOFILL VALUES
            # We map values into the 'sign.request.item.value' model
            # =========================================================
            try:
                for template_field in template.sign_item_ids:
                    if template_field.name in replacements and replacements[template_field.name]:
                        # Find the signer record corresponding to this field's role
                        signer_record = sign_request.request_item_ids.filtered(
                            lambda r: r.role_id.id == template_field.responsible_id.id
                        )
                        
                        if signer_record:
                            self.env['sign.request.item.value'].create({
                                'sign_request_item_id': signer_record[0].id,
                                'sign_item_id': template_field.id,
                                'value': str(replacements[template_field.name]),
                            })
            except Exception as e:
                # If autofill fails, log it, but don't break document generation
                _logger.warning(f"Failed to autofill values for sign request {sign_request.id}: {e}")

            # =========================================================
            # STEP 4: LINK
            # Removed action_sent() for Odoo 17 compatibility
            # =========================================================
            commitment.sign_request_id = sign_request.id
            generated_requests |= sign_request

        if not generated_requests:
            return True

        # Open the generated documents for the user to see
        action = self.env['ir.actions.actions']._for_xml_id('sign.sign_request_action')
        if len(generated_requests) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': generated_requests.id,
                'views': [(False, 'form')],
            })
        else:
            action['domain'] = [('id', 'in', generated_requests.ids)]
        
        return action
