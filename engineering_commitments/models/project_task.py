# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, _, api
from odoo.exceptions import UserError
import datetime # Make sure datetime is imported for timestamps

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

    # -- THE FINAL CORRECT CODE - Programmatic Signing to preserve original design --
    def action_generate_commitments_pdf(self):
        self.ensure_one()

        required_commitments = self.commitment_ids.filtered(lambda p: p.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as 'Required' first."))

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("The project must have a Customer to generate documents."))

        # This role is still important for identifying which fields belong to the customer
        role_customer = self.env.ref('sign.sign_item_role_customer', raise_if_not_found=False)
        # We need a system user to "sign" on behalf of the customer, if no specific partner is intended to sign.
        # Often, the current user or a generic system user is used for programmatic completion.
        # For simplicity, we'll use the current user for internal "signatures" and the customer's partner for customer fields.
        current_partner = self.env.user.partner_id 

        # 1. GET VALUES FROM PROJECT
        replacements = {
            'Name': project.partner_id.name or "NO NAME",
            'Date': fields.Date.context_today(self).strftime("%Y/%m/%d"),
            'Governorate': project.governorate_id.name if project.governorate_id else "NO GOV",
            'Region': project.region_id.name if project.region_id else "NO REGION",
            'Block': project.block_no or "NO BLOCK",
            'Plot': project.plot_no or "NO PLOT",
            # Add fields for programmatic signatures if they exist in your templates as text fields
            # Example: If you have a text field named 'Customer Signature Text' on your template
            'Customer Signature Text': project.partner_id.name or "N/A", 
            'Signature Date Text': fields.Date.context_today(self).strftime("%Y/%m/%d"),
            'Company Signature Text': self.env.user.company_id.name or "N/A", # Example for company signature
        }

        generated_requests = self.env['sign.request']

        for commitment in required_commitments:
            # Check if an existing request is already completed/signed, if so, skip or recreate
            if commitment.sign_request_id and commitment.sign_request_id.state in ('signed', 'completed'):
                _logger.info(f"Skipping commitment {commitment.sign_template_id.name} as request {commitment.sign_request_id.name} is already signed.")
                generated_requests |= commitment.sign_request_id
                continue
            elif commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                # If it's not signed/completed but exists (e.g., pending), let's cancel it and create a new one
                _logger.info(f"Canceling existing pending sign request {commitment.sign_request_id.name} for {commitment.sign_template_id.name}.")
                commitment.sign_request_id.cancel()
                commitment.sign_request_id = False # Clear the link to create a new one

            template = commitment.sign_template_id
            
            # STEP 1: Create the Sign Request
            # Crucially, set `state` to 'sent' but `mail_sent` to False to prevent immediate emails.
            # We'll then immediately mark it as signed.
            roles = template.sign_item_ids.mapped('responsible_id')
            signers_list_vals = []
            for role in roles:
                # Assign partner for each role. Customer role gets project.partner_id, others get current user's partner.
                partner_to_assign = project.partner_id if (role_customer and role.id == role_customer.id) else current_partner
                signers_list_vals.append((0, 0, {
                    'role_id': role.id,
                    'partner_id': partner_to_assign.id,
                }))

            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {project.name}",
                'request_item_ids': signers_list_vals,
                'state': 'sent', # Important: Create in 'sent' state before marking as signed
                'mail_sent': False, # Prevent initial email sending
                'signer_ids': [(6, 0, [item['partner_id'] for item in signers_list_vals if item['partner_id']])]
            })

            # STEP 2: Fill the fields with data
            for template_field in template.sign_item_ids:
                field_name = template_field.name
                if field_name in replacements:
                    value_to_insert = replacements[field_name]
                    
                    # Find the corresponding signer record for this field's responsible role
                    signer_record = sign_request.request_item_ids.filtered(
                        lambda r: r.role_id.id == template_field.responsible_id.id
                    )
                    
                    if signer_record:
                        # Ensure the value is set for the correct signer's field
                        self.env['sign.request.item.value'].sudo().create({
                            'sign_request_item_id': signer_record[0].id,
                            'sign_item_id': template_field.id,
                            'value': value_to_insert,
                        })

            # STEP 3: Programmatically "Sign" all request items (roles) in the sign_request
            for request_item in sign_request.request_item_ids:
                if request_item.state == 'sent': # Only sign if not already signed or canceled
                    request_item.write({
                        'state': 'signed',
                        'signed_by': request_item.partner_id.id, # The partner assigned to this role
                        'signed_on': fields.Datetime.now(),
                    })
            
            # Update the main sign_request state if all items are signed
            sign_request._compute_state() # Recalculate the state of the parent request

            commitment.sign_request_id = sign_request.id
            generated_requests |= sign_request

        if not generated_requests:
            return True

        # Return action to view the completed (programmatically signed) sign requests
        action = self.env['ir.actions.actions']._for_xml_id('sign.sign_request_action')
        if len(generated_requests) == 1:
            action.update({'view_mode': 'form', 'res_id': generated_requests.id, 'views': [(False, 'form')]})
        else:
            action['domain'] = [('id', 'in', generated_requests.ids)]
        
        return action
