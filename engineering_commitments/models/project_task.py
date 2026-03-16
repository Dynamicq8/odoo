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
        # This method remains unchanged.
        # It's not directly used by the TEST code below, but kept for completeness.
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
        """ 
        TEMPORARY TEST VERSION: 
        Creates a single Sign Request using a simple test template and auto-fills variables.
        This bypasses your 'required_commitments' loop to isolate the PDF issue.
        """
        self.ensure_one()

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("The project must have a Customer to generate documents. (يجب تحديد عميل للمشروع)"))

        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        if not role_customer:
            raise UserError(_("Error: The 'Customer' role could not be found in the Sign application. Please check its configuration."))

        # --- AUTOFILL DICTIONCTIONARY (for testing, these might not be used if template is too simple) ---
        replacements = {
            'Name': project.partner_id.name or "Test Customer", # Added default for safety
            'Date': fields.Date.context_today(self).strftime("%Y/%m/%d"),
            'Governorate': project.governorate_id.name if hasattr(project, 'governorate_id') and project.governorate_id else "",
            'Region': project.region_id.name if hasattr(project, 'region_id') and project.region_id else "",
            'Block': project.block_no or "" if hasattr(project, 'block_no') else "",
            'Plot': project.plot_no or "" if hasattr(project, 'plot_no') else "",
            'Street': project.street_no or "" if hasattr(project, 'street_no') else "",
        }

        # --- TEST-SPECIFIC CODE: Find and use the simple test template ---
        test_template_name = '__TEST__ Simple Commitment Template' 
        template = self.env['sign.template'].search([('name', '=', test_template_name)], limit=1)
        if not template:
            raise UserError(_(f"TEST FAILED: Template '{test_template_name}' not found! "
                              f"Please create it first as per instructions."))

        _logger.info(f"Processing TEST commitment for template: {template.name} (ID: {template.id})")
        _logger.info(f"Number of sign items on TEST template before creating request: {len(template.sign_item_ids)}")

        if not template.sign_item_ids:
            _logger.warning(f"TEST FAILED: Template '{template.name}' has no sign items defined. "
                            f"Please ensure you dragged at least ONE Signature field onto it. Skipping.")
            return True # Indicates the test template itself is misconfigured

        # 1. Create the Sign Request from the template.
        sign_request = self.env['sign.request'].create({
            'template_id': template.id,
            'reference': f"{template.name} - {project.name} (TEST REQUEST)",
        })
        
        _logger.info(f"Created sign request {sign_request.id} from TEST template {template.name}.")
        _logger.info(f"Number of request items on the NEWLY CREATED TEST sign request: {len(sign_request.request_item_ids)}")

        # --- CRITICAL CHECK FOR THIS ERROR ---
        if not sign_request.request_item_ids:
            _logger.error(
                f"Validation Error (TEST FAILED): Sign request {sign_request.id} (from TEST template '{template.name}') "
                f"has NO items after creation. This confirms an issue with the PDF document or Odoo's processing of it. "
                f"Try a different, simpler PDF. Deleting the empty sign request."
            )
            sign_request.unlink() # Clean up the empty request
            raise UserError(_(
                f"TEST FAILED: The sign request for '{template.name}' could not be created with items. "
                f"This indicates a problem with the PDF document itself. Please try a simpler PDF."
            ))

        # 2. Assign the partner to the items with the 'Customer' role.
        customer_items = sign_request.request_item_ids.filtered(
            lambda item: item.role_id.id == role_customer.id
        )
        if customer_items:
            customer_items.write({'partner_id': project.partner_id.id})
        else:
            _logger.warning(f"No customer-assigned items found for TEST sign request {sign_request.id}. (Ensure Signature field is assigned to Customer role)")

        # 3. Loop through items to fill values (only if they match a replacement key).
        for item in sign_request.request_item_ids:
            if item.name and item.name in replacements:
                item.write({'value': replacements[item.name]})

        # 4. Send the request.
        sign_request.action_sent()
        
        # NOTE: Since this is a test, we are not linking it to an 'engineering.task.commitment' record.
        # You'll manually delete this test sign request later.

        # Return an action to open the generated TEST document for the user
        action = self.env['ir.actions.actions']._for_xml_id('sign.sign_request_action')
        action.update({
            'view_mode': 'form',
            'res_id': sign_request.id,
            'views': [(False, 'form')],
        })
        _logger.info(f"Returning action for generated TEST request: {sign_request.id}")
        return action
