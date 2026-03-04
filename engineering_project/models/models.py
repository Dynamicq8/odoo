# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import urllib.parse

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # The project holds the main data (copied from the Quotation)
    sale_order_id = fields.Many2one('sale.order', string='Source Quotation', readonly=True)
    building_type = fields.Selection([...], string="نوع المبنى") # Keep your selection
    service_type = fields.Selection([...], string="نوع الخدمة") # Keep your selection
    region = fields.Char(string="المنطقة (Region)")
    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الشارع")
    area = fields.Char(string="المساحة (Area)")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # --- THE FIELDS ARE MOVED HERE, TO THE TASK ---
    floor_basement = fields.Text(string="أولاً السرداب")
    floor_ground = fields.Text(string="ثانياً الدور الأرضي")
    floor_first = fields.Text(string="الدور الأول")
    floor_second = fields.Text(string="الدور الثاني")
    floor_roof = fields.Text(string="الدور السطح")
    
    # This button lets you go back to the main project easily
    def action_view_parent_project(self):
        self.ensure_one()
        if not self.project_id:
            raise UserError(_("This task is not linked to any Project."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # --- THE WHATSAPP BUTTON LOGIC IS MOVED HERE ---
    def action_send_task_form_whatsapp(self):
        self.ensure_one()
        phone = self.project_id.partner_id.mobile or self.project_id.partner_id.phone
        if not phone:
            raise UserError("رقم الهاتف مفقود للعميل")
        
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        
        # We need a portal view for tasks for this to work perfectly,
        # but for now, we send a message asking them to check their email.
        # Alternatively, we can attach the PDF to an email and send it.
        message = _("مرحباً %s،\nتم تحديث تفاصيل المهمة '%s' الخاصة بمشروعكم. يرجى المراجعة.") % (self.project_id.partner_id.name, self.name)
        
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"
        
        return { 'type': 'ir.actions.act_url', 'url': whatsapp_url, 'target': 'new' }
