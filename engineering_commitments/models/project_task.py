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
            raise UserError("Please mark at least one commitment as 'Required' first.")
            
        template = required_commitments[0].sign_template_id
        if not template.sign_item_ids:
            raise UserError(f"Template '{template.name}' has no fields configured.")
            
        # ==========================================
        # DIAGNOSTIC X-RAY
        # ==========================================
        xray_report = "Here are the exact secret names Odoo is using for your fields:\n\n"
        
        for item in template.sign_item_ids:
            field_name = str(item.name or 'EMPTY')
            field_type = str(item.type_id.name or 'EMPTY')
            xray_report += f"Box -> Name: '{field_name}'  |  Type: '{field_type}'\n"
            
        xray_report += "\nTake a screenshot of this popup and send it to me!"
        
        # This will forcefully pop up a window on your screen
        raise UserError(xray_report)
