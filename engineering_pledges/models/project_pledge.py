# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

# 1. Add our custom fields to Odoo's native Sign Template
class SignTemplate(models.Model):
    _inherit = 'sign.template'

    building_type = fields.Selection([
        ('residential', 'سكن خاص'), ('investment', 'استثماري'), 
        ('commercial', 'تجاري'), ('industrial', 'صناعي'), 
        ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), 
        ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع'), ('all', 'جميع الأنواع')
    ], string="نوع العقار (Building Type)", default='all')
    
    is_municipality_pledge = fields.Boolean(string="تعهد بلدية؟", default=False)

# 2. Update the Pledge Line to link to Sign templates
class EngineeringTaskPledge(models.Model):
    _name = 'engineering.task.pledge' 
    _description = 'Task Municipality Pledge'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    # Link to Odoo's Sign Template instead of HTML template
    sign_template_id = fields.Many2one('sign.template', string='نوع التعهد (Pledge PDF)', required=True, domain=[('is_municipality_pledge', '=', True)])
    is_completed = fields.Boolean(string='متوفر / مطلوب (Required)', default=False)
    
    # Store the generated document so we can track it
    sign_request_id = fields.Many2one('sign.request', string='المستند المولد (Generated Doc)', readonly=True)

# 3. Update the Project Task
class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_sequence = fields.Integer(related='stage_id.sequence', readonly=True)
    pledge_ids = fields.One2many('engineering.task.pledge', 'task_id', string='تعهدات البلدية (Pledges)')

    def action_load_required_pledges(self):
        """ Loads PDF Sign templates based on the project's building type """
        for task in self:
            building_type = task.project_id.building_type
            if not building_type:
                continue

            # Find Sign Templates that are marked as pledges and match the building type
            domain = [('is_municipality_pledge', '=', True), ('building_type', 'in', [building_type, 'all'])]
            templates = self.env['sign.template'].search(domain)
            
            existing_template_ids = task.pledge_ids.mapped('sign_template_id.id')
            
            for template in templates:
                if template.id not in existing_template_ids:
                    self.env['engineering.task.pledge'].create({
                        'task_id': task.id,
                        'sign_template_id': template.id,
                    })

    def action_generate_pledges_pdf(self):
        """ 
        1. Finds all completed pledges.
        2. Creates a Sign Request for each.
        3. Auto-fills the variables based on the field names in the PDF.
        """
        self.ensure_one()
        
        completed_pledges = self.pledge_ids.filtered(lambda p: p.is_completed)
        if not completed_pledges:
            raise UserError(_("عفواً، يرجى تفعيل خيار 'مطلوب' بجانب التعهد المطلوب أولاً."))

        project = self.project_id
        
        # --- IMPORTANT FIX 1: Ensure project has a partner ---
        if not project.partner_id:
            raise UserError(_("لا يمكن إنشاء تعهدات بدون عميل مرتبط بالمشروع. يرجى تعيين عميل للمشروع أولاً."))
        
        # Store the partner ID for use in sign_request_items
        project_partner_id = project.partner_id.id

        # Prepare the variables dictionary. 
        # IMPORTANT: The keys here MUST match the "Name" you give to the text fields inside the Odoo Sign App.
        replacements = {
            'partner_name': project.partner_id.name or "",
            'date': datetime.date.today().strftime("%Y/%m/%d"),
            'governorate': project.governorate_id.name if project.governorate_id else "",
            'region': project.region_id.name if project.region_id else "",
            'block_no': project.block_no or "",
            'plot_no': project.plot_no or "",
            'street_no': project.street_no or "",
        }

        # Get the default role (usually Customer/Partner) to assign the document to
        role_id = self.env.ref('sign.sign_item_role_customer').id

        generated_requests = self.env['sign.request']

        for pledge in completed_pledges:
            if pledge.sign_request_id and pledge.sign_request_id.state != 'canceled':
                # If a document is already generated for this line, just add it to the list to view later
                generated_requests |= pledge.sign_request_id
                continue

            template = pledge.sign_template_id
            
            # Prepare auto-filled items for the Sign Request
            sign_request_items = []
            for item in template.sign_item_ids:
                # --- IMPORTANT FIX 2: Add partner_id to each sign_request_item ---
                item_vals = {
                    'role_id': role_id,
                    'sign_item_id': item.id,
                    'partner_id': project_partner_id, # This links the item to the project's partner
                }
                
                # If the name of the field you dragged in the Sign app matches our dictionary, pre-fill it
                if item.name in replacements:
                    item_vals['value'] = str(replacements[item.name])
                
                sign_request_items.append((0, 0, item_vals))

            # Create the actual Sign Request (The Document)
            sign_request = self.env['sign.request'].create({
                'template_id': template.id,
                'reference': f"{template.name} - {project.name}",
                # --- IMPORTANT FIX 3: Remove 'approver_id' from here ---
                'request_item_ids': sign_request_items,
                'state': 'sent', # Mark as ready/sent
            })

            # Link the generated document to the pledge line
            pledge.sign_request_id = sign_request.id
            generated_requests |= sign_request

        # Action to open the generated Sign Requests so the user can see/print them
        if len(generated_requests) == 1:
            return generated_requests.go_to_document()
        else:
            return {
                'name': 'Generated Pledges',
                'type': 'ir.actions.act_window',
                'res_model': 'sign.request',
                'view_mode': 'kanban,tree,form',
                'domain': [('id', 'in', generated_requests.ids)],
            }
