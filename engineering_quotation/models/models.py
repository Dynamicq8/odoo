 # -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import urllib.parse

class EngineeringQuotationStage(models.Model):
    _name = 'engineering.quotation.stage'
    _description = 'Engineering Quotation Stage'
    _order = 'sequence, id'

    name = fields.Char(string='اسم المرحلة', required=True, translate=True)
    sequence = fields.Integer(default=10)
    next_stage_id = fields.Many2one('engineering.quotation.stage', string="المرحلة التالية")
    button_name = fields.Char(string="نص الزر")
    is_approved_stage = fields.Boolean(string="مرحلة الموافقة؟")
    is_rejected_stage = fields.Boolean(string="مرحلة الرفض؟")
    fold = fields.Boolean(string='Folded in Kanban', default=False)


class EngineeringQuotationStageHistory(models.Model):
    _name = 'engineering.quotation.stage.history'
    _description = 'Quotation Stage History'
    _order = 'change_date desc'

    quotation_id = fields.Many2one('sale.order', string='Quotation', ondelete='cascade')
    from_stage_id = fields.Many2one('engineering.quotation.stage', string='From Stage')
    to_stage_id = fields.Many2one('engineering.quotation.stage', string='To Stage')
    changed_by_id = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user)
    change_date = fields.Datetime(string='Change Date', default=fields.Datetime.now)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")

    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الشارع")
    area = fields.Char(string="مساحة الارض")

    project_id = fields.Many2one('project.project', string='Project', copy=False)
    
    quotation_stage_id = fields.Many2one(
        'engineering.quotation.stage',
        string='Quotation Stage',
        tracking=True,
        default=lambda self: self.env['engineering.quotation.stage'].search([], order='sequence', limit=1)
    )
    stage_history_ids = fields.One2many('engineering.quotation.stage.history', 'quotation_id', string='Stage History')
    
    next_stage_button_name = fields.Char(compute='_compute_next_stage_button_name')
    show_next_stage_button = fields.Boolean(compute='_compute_next_stage_button_name')

    required_documents = fields.Html(string="المستندات المطلوبة", compute='_compute_required_documents', store=True)

    @api.depends('service_type', 'building_type')
    def _compute_required_documents(self):
        for order in self:
            docs = "<ul>"
            docs += "<li>البطاقة المدنية للمالك (Civil ID Copy)</li>"
            if order.service_type == 'new_construction':
                docs += "<li>وثيقة الملكية</li><li>كتاب التخصيص</li><li>مخطط المساحة</li>"
            elif order.service_type in ['modification', 'addition', 'addition_modification']:
                docs += "<li>رخصة البناء الأصلية</li><li>المخططات المرخصة</li><li>وثيقة البيت</li>"
            elif order.service_type == 'demolition':
                docs += "<li>كتاب براءة ذمة من الكهرباء والماء</li><li>رخصة البناء القديمة</li>"
            docs += "</ul>"
            order.required_documents = docs

    def action_confirm(self):
        for order in self:
            if order.signature:
                approved_stage = self.env['engineering.quotation.stage'].search([('is_approved_stage', '=', True)], limit=1)
                if approved_stage and order.quotation_stage_id != approved_stage:
                    order.quotation_stage_id = approved_stage.id
        return super(SaleOrder, self).action_confirm()

    def action_move_to_next_stage(self):
        self.ensure_one()
        current_stage = self.quotation_stage_id
        next_stage = current_stage.next_stage_id if current_stage else False
        if next_stage:
            self.env['engineering.quotation.stage.history'].create({
                'quotation_id': self.id,
                'from_stage_id': current_stage.id if current_stage else False,
                'to_stage_id': next_stage.id,
            })
            self.write({'quotation_stage_id': next_stage.id})
            if next_stage.is_approved_stage:
                return {'effect': {'fadeout': 'slow', 'message': _('تمت الموافقة على عرض السعر!'), 'type': 'rainbow_man'}}
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return True

    def action_create_project_from_quotation(self):
        self.ensure_one()
        if self.project_id: return
        project = self._create_engineering_project()
        return {
            'type': 'ir.actions.act_window',
            'name': _('المشروع (Project)'),
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _create_engineering_project(self):
        self.ensure_one()
        project_vals = {
            'name': f"{self.name} - {self.partner_id.name}",
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'building_type': self.building_type,
            'service_type': self.service_type,
            'plot_no': self.plot_no,
            'block_no': self.block_no,
            'street_no': self.street_no,
            'area': self.area,
                  # Update these keys to match the new fields:
        'governorate_id': self.governorate_id.id, 
        'region_id': self.region_id.id,
        }
        project = self.env['project.project'].create(project_vals)
        
         # --- FIXED STAGES TO MATCH YOUR IMAGE EXACTLY ---
        stages = [
            'التصميم المبدئي', 
            'التعاقد والوثائق', 
            'المخطط الانشائي', 
            'الموافقات', 
            'التصميمات التفصيلية', 
            'الإشراف', 
            'إنهاء المشروع'
        ]
        for index, stage_name in enumerate(stages):
            self.env['project.task.type'].create({
                'name': stage_name, 
                'project_ids': [(4, project.id)], 
                'sequence': index + 1
            })
            
        self.write({'project_id': project.id})
        return project

    @api.depends('quotation_stage_id', 'state')
    def _compute_next_stage_button_name(self):
        for order in self:
            order.show_next_stage_button = bool(order.quotation_stage_id.next_stage_id and order.state != 'cancel')
            order.next_stage_button_name = order.quotation_stage_id.button_name

    def action_send_quotation_whatsapp(self):
        self.ensure_one()
        phone = self.partner_id.mobile or self.partner_id.phone
        if not phone: raise UserError(_("رقم الهاتف مفقود"))
        self._portal_ensure_token()
        link = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + self.get_portal_url()
        msg = urllib.parse.quote(_("مرحباً %s، يرجى مراجعة عرض السعر %s: %s") % (self.partner_id.name, self.name, link))
        return {'type': 'ir.actions.act_url', 'url': f"https://web.whatsapp.com/send?phone={phone}&text={msg}", 'target': 'new'}

    def action_create_opening_fee_invoice(self):
        self.ensure_one()
        product_fee = self.env['product.product'].search([('name', '=', 'رسوم فتح ملف')], limit=1)
        if not product_fee:
            product_fee = self.env['product.product'].create({'name': 'رسوم فتح ملف', 'type': 'service', 'list_price': 50.0})
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {'product_id': product_fee.id, 'quantity': 1, 'price_unit': 50.0, 'name': 'رسوم فتح ملف وتصميم مبدئي'})],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return {'name': _('Open Invoice'), 'view_mode': 'form', 'res_model': 'account.move', 'res_id': invoice.id, 'type': 'ir.actions.act_window'}

    def action_apply_opening_deduction(self):
        self.ensure_one()
        product_fee = self.env['product.product'].search([('name', '=', 'رسوم فتح ملف')], limit=1)
        if not product_fee: raise UserError(_("Product 'رسوم فتح ملف' not found."))
        self.env['sale.order.line'].create({
            'order_id': self.id,
            'product_id': product_fee.id,
            'name': 'خصم رسوم فتح ملف',
            'product_uom_qty': 1,
            'price_unit': -50.0,
            'tax_id': False,
        })
        return True


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Quotation Source', readonly=True)
    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")
    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الشارع")
    area = fields.Char(string="مساحة الارض")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_view_parent_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
