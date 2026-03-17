# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, _, api
from odoo.exceptions import UserError
import datetime # Import datetime for current timestamp in QWeb (already used indirectly by fields.Date.context_today)

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

    # -- THE FINAL CORRECT CODE FOR OPTION 2 - DIRECT PDF GENERATION --
    def action_generate_commitments_pdf(self):
        self.ensure_one()

        required_commitments = self.commitment_ids.filtered(lambda p: p.is_required)
        if not required_commitments:
            raise UserError(_("Please mark at least one commitment as 'Required' first."))

        project = self.project_id
        if not project.partner_id:
            raise UserError(_("The project must have a Customer to generate documents."))
            
        # Instead of creating sign.request, we will directly generate a PDF report.
        # The 'sign.template' records are still used to define the *list* of commitments,
        # but their content isn't used for filling fields in the PDF here.
        # The QWeb report itself dictates the content.

        # Trigger the custom QWeb PDF report for the current project.task
        # The 'self' record (project.task) will be passed as 'docs' to the QWeb template.
        return self.env.ref('your_module_name.action_report_project_commitment').report_action(self)
