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
        """ Attempts to create Sign Requests by creating the request first, then adding items. """
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
            # Skip if already generated and not canceled
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                generated_requests |= commitment.sign_request_id
                continue

            template = commitment.sign_template_id
            if not template.sign_item_ids:
                raise UserError(_(f"Template '{template.name}' has no fields/signature configured. Please add them in the Sign app."))

            _logger.info(f"Attempting to create sign.request for template: {template.name} (ID: {template.id}) - Strategy: Create request, then add items.")

            # ====================================================================
            # EXPERIMENTAL STRATEGY: Create sign.request first (without items),
            # then add items via write.
            # ====================================================================
            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {project.name}",
                # Do NOT include 'request_item_ids' here yet
            })
            _logger.info(f"Successfully created empty sign request: {sign_request.id}.")

            # Now, prepare the items to add
            request_item_vals_list = []
            for template_item in template.sign_item_ids:
                partner_id = project.partner_id.id if template_item.responsible_id.id == role_customer.id else False
                value = replacements.get(template_item.name, "") if template_item.name else ""

                # Using 'sign_item_type_id' again here, as it's the most standard
                # If this fails, we NEED to know the actual field name from developer tools.
                item_vals = {
                    'sign_item_type_id': template_item.type_id.id, # <--- Re-attempting this standard field name
                    'name': template_item.name,
                    'required': template_item.required,
                    'responsible_id': template_item.responsible_id.id,
                    'partner_id': partner_id,
                    'page': template_item.page,
                    'posX': template_item.posX,
                    'posY': template_item.posY,
                    'width': template_item.width,
                    'height': template_item.height,
                    'value': str(value),
                }
                _logger.info(f"Prepared item values for write: {item_vals}")
                request_item_vals_list.append((0, 0, item_vals))

            # Attempt to write the items to the newly created sign_request
            _logger.info(f"Attempting to write request_item_ids to sign_request {sign_request.id}")
            try:
                sign_request.write({'request_item_ids': request_item_vals_list})
                _logger.info(f"Successfully wrote request_item_ids to sign_request {sign_request.id}")
            except Exception as e:
                _logger.error(f"Failed to write request_item_ids to sign_request {sign_request.id}: {e}")
                sign_request.unlink() # Clean up the request if item creation failed
                raise UserError(_(f"Failed to add items to the sign request. This usually means a field name for the sign item type is incorrect, or a required field is missing. Original error: {e}"))


            # After creation, iterate through the *newly created* request items
            # to apply the autofill values. (This loop is technically redundant now
            # since we set values during write, but kept for consistency)
            # for item in sign_request.request_item_ids:
            #     if item.name and item.name in replacements:
            #         item.write({'value': replacements[item.name]})

            # Send the request
            sign_request.action_sent()

            # Link document to the task line
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
