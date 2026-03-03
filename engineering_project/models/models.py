# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Source Quotation', readonly=True)
    
    # Engineering specific fields
    building_type = fields.Selection(related='sale_order_id.building_type', store=True, string="نوع المبنى")
    service_type = fields.Selection(related='sale_order_id.service_type', store=True, string="نوع الخدمة")
    
    # Region
    region = fields.Selection(related='sale_order_id.region', store=True, string="المنطقة (Region)")
    
    # Location Details
    plot_no = fields.Char(related='sale_order_id.plot_no', store=True, string="رقم القسيمة")
    block_no = fields.Char(related='sale_order_id.block_no', store=True, string="القطعة")
    
    # --- THIS WAS MISSING ---
    street_no = fields.Char(related='sale_order_id.street_no', store=True, string="الشارع") 
    # ------------------------

    area = fields.Char(related='sale_order_id.area', store=True, string="المساحة (Area)")


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
