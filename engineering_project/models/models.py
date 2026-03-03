# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Source Quotation', readonly=True)
    
    # We REMOVED 'related'. These are now standard fields that can store data.
    building_type = fields.Selection([
        ('residential', 'سكن خاص'), ('investment', 'استثماري'), 
        ('commercial', 'تجاري'), ('industrial', 'صناعي'), 
        ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), 
        ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')
    ], string="نوع المبنى")

    service_type = fields.Selection([
        ('new_construction', 'بناء جديد'), ('demolition', 'هدم'), 
        ('modification', 'تعديل'), ('addition', 'اضافة'), 
        ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), 
        ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), 
        ('shades_garden', 'مظلات / حدائق')
    ], string="نوع الخدمة")
    
    region = fields.Char(string="المنطقة (Region)")
    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الشارع")
    area = fields.Char(string="المساحة (Area)")


class ProjectTask(models.Model):
    _inherit = 'project.task'

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
