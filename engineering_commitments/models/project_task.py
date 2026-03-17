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
        # 1. GET VALUES (I left the "NO DATA" warnings so you know if your Project is empty!)
        # ==========================================
        val_name = project.partner_id.name or "NO NAME"
        val_date = fields.Date.context_today(self).strftime("%Y/%m/%d")
        val_gov = project.governorate_id.name if project.governorate_id else "NO GOV"
        val_region = project.region_id.name if project.region_id else "NO REGION"
        val_block = project.block_no or "NO BLOCK"
        val_plot = project.plot_no or "NO PLOT"

        # These match your X-Ray results EXACTLY
        replacements = {
            'Name': val_name,
            'Date': val_date,
            'Governorate': val_gov,
            'Region': val_region,
            'Block': val_block,
            'Plot': val_plot,
        }

        generated_requests = self.env['sign.request']

        for commitment in required_commitments:
            if commitment.sign_request_id and commitment.sign_request_id.state != 'canceled':
                generated_requests |= commitment.sign_request_id
                continue

            template = commitment.sign_template_id
            if not template.sign_item_ids:
                raise UserError(_(f"Template '{template.name}' has no fields configured."))

            # 2. Define Signers
            roles = template.sign_item_ids.mapped('responsible_id')
            signers_list = []
            for role in roles:
                partner_id = project.partner_id.id if (role_customer and role.id == role_customer.id) else self.env.user.partner_id.id
                signers_list.append((0, 0, {
                    'role_id': role.id,
                    'partner_id': partner_id,
                }))

            # 3. Create Request (THIS automatically generates empty boxes in Odoo)
            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {project.name}",
                'request_item_ids': signers_list,
            })

            # 4. THE FIX: Find Odoo's empty boxes and overwrite them!
            for template_field in template.sign_item_ids:
                field_name = template_field.name
                
                if field_name in replacements:
                    val_to_insert = replacements[field_name]
                    
                    if val_to_insert:
                        # Search for the auto-generated empty box
                        existing_value = self.env['sign.request.item.value'].sudo().search([
                            ('sign_item_id', '=', template_field.id),
                            ('sign_request_item_id.sign_request_id', '=', sign_request.id)
                        ], limit=1)
                        
                        if existing_value:
                            # IF WE FIND IT: Update it with our text!
                            existing_value.write({'value': str(val_to_insert)})
                        else:
                            # FAILSAFE: If Odoo didn't make one, we create it.
                            signer_record = sign_request.request_item_ids.filtered(
                                lambda r: r.role_id.id == template_field.responsible_id.id
                            )
                            if signer_record:
                                self.env['sign.request.item.value'].sudo().create({
                                    'sign_request_item_id': signer_record[0].id,
                                    'sign_item_id': template_field.id,
                                    'value': str(val_to_insert),
                                })

            commitment.sign_request_id = sign_request.id
            generated_requests |= sign_request

        if not generated_requests:
            return True

        # 5. Open the Document
        action = self.env['ir.actions.actions']._for_xml_id('sign.sign_request_action')
        if len(generated_requests) == 1:
            action.update({'view_mode': 'form', 'res_id': generated_requests.id, 'views': [(False, 'form')]})
        else:
            action['domain'] = [('id', 'in', generated_requests.ids)]
        
        return action
