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
            # Assuming your project has a building_type field. If not, this acts as a safeguard.
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
        """ Creates Sign Requests and auto-fills variables for required commitments. """
        self.ensure_one()

        required_commitments = self.commitment_ids.filtered(lambda p: p.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as 'Required' first. (يرجى تحديد تعهد واحد على الأقل كمطلوب)"))

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("The project must have a Customer to generate documents. (يجب تحديد عميل للمشروع)"))

        # Find the default 'Customer' role for signing
        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        if not role_customer:
            raise UserError(_("Error: The 'Customer' role could not be found in the Sign application. Please check its configuration."))

        # --- AUTOFILL DICTIONARY ---
        # The keys here ('Name', 'Date', etc.) MUST match the 'Field Name'
        # you set on the Text fields in your Sign Template.
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
            # Skip if already generated and not canceled
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                generated_requests |= commitment.sign_request_id
                continue

            template = commitment.sign_template_id
            if not template.sign_item_ids:
                _logger.warning(f"Template '{template.name}' has no sign items defined and will be skipped.")
                continue

            # --- THE CORRECT APPROACH ---

            # 1. Create the Sign Request from the template with the signer.
            #    Odoo automatically copies the sign items from the template.
            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {project.name}",
                'signer_ids': [(0, 0, {
                    'role_id': role_customer.id,
                    'partner_id': project.partner_id.id,
                })],
            })

            # 2. Loop through the NEWLY created request items and fill in the values.
            for item in sign_request.request_item_ids:
                # The 'name' of the sign item in the template is copied over.
                # We check if this name is a key in our replacements dictionary.
                if item.name and item.name in replacements:
                    item.write({'value': replacements[item.name]})

            # 3. Now that values are filled, send the request. This changes the state to 'sent'.
            sign_request.action_sent()

            # Link document to the task line and collect it for the final action
            commitment.sign_request_id = sign_request.id
            generated_requests |= sign_request

        # If no new documents were generated, do nothing.
        if not generated_requests:
            return True

        # --- Return an action to open the generated documents for the user ---
        action = self.env['ir.actions.actions']._for_xml_id('sign.sign_request_action')
        
        if len(generated_requests) == 1:
            # If only one was created, open it directly in form view
            action.update({
                'view_mode': 'form',
                'res_id': generated_requests.id,
                'views': [(False, 'form')],
            })
        else:
            # If multiple were created, open them in a list view
            action['domain'] = [('id', 'in', generated_requests.ids)]
        
        return action
