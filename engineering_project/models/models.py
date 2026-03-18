# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import urllib.parse

# ==============================================================================
#  WORKFLOW TEMPLATES (خرائط سير العمل)
# ==============================================================================
WORKFLOW_TEMPLATES = {
    # 1. سكن خاص + بناء جديد
    'res_new':[
        {'code': 'rn_1_1', 'name': '1- تصميم الكروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'rn_1_2', 'name': '2- تجميع المستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'rn_1_3', 'name': '3- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        {'code': 'rn_1_4', 'name': '4- تجهيز النماذج والتعهدات والتوقيع', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'rn_1_5', 'name': '5- فحص التربة - كتاب الكهرباء', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},

        {'code': 'rn_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'rn_2_2', 'name': '2- الواجهات', 'stage': 'المرحلة الثانية', 'role': 'facade_draftsman_id'},
        {'code': 'rn_2_3', 'name': '3- رسم مخطط البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},

        {'code': 'rn_3_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'rn_3_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'rn_3_3', 'name': '3- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},

        {'code': 'rn_4_1', 'name': '1- تصميم المخطط الإنشائي', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'rn_4_2', 'name': '2- تصميم مخطط الصحي', 'stage': 'المرحلة الرابعة', 'role': 'draftsman_id'},
        {'code': 'rn_4_3', 'name': '3- تصميم مخطط الكهرباء', 'stage': 'المرحلة الرابعة', 'role': 'electrical_id'},
        {'code': 'rn_4_4', 'name': '4- تصميم مخطط الفرش', 'stage': 'المرحلة الرابعة', 'role': 'architect_id'},
        {'code': 'rn_4_5', 'name': '5- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},

        {'code': 'rn_5_1', 'name': '1- إصدار تعهد الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'rn_5_2', 'name': '2- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'rn_5_3', 'name': '3- كتب البنك', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'rn_5_4', 'name': '4- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],

    # 2. غير سكني (استثماري، صناعي، إلخ) + بناء جديد
    'non_res_new':[
        {'code': 'nrn_1_1', 'name': '1- تصميم الكروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'nrn_1_2', 'name': '2- تجميع المستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'nrn_1_3', 'name': '3- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        {'code': 'nrn_1_4', 'name': '4- تجهيز النماذج والتعهدات والتوقيع', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'nrn_1_5', 'name': '5- فحص التربة - كتاب الكهرباء', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},

        {'code': 'nrn_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'nrn_2_2', 'name': '2- الواجهات', 'stage': 'المرحلة الثانية', 'role': 'facade_draftsman_id'},
        {'code': 'nrn_2_3', 'name': '3- رسم مخطط البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},

        {'code': 'nrn_3_1', 'name': '1- إرسال للمطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_2', 'name': '2- اعتماد المطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_3', 'name': '3- إرسال للتنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_4', 'name': '4- اعتماد التنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_5', 'name': '5- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_6', 'name': '6- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nrn_3_7', 'name': '7- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},

        {'code': 'nrn_4_1', 'name': '1- تصميم المخطط الإنشائي', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'nrn_4_2', 'name': '2- تصميم مخطط الصحي', 'stage': 'المرحلة الرابعة', 'role': 'draftsman_id'},
        {'code': 'nrn_4_3', 'name': '5- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},

        {'code': 'nrn_5_1', 'name': '1- إصدار تعهد الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'nrn_5_2', 'name': '2- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'nrn_5_3', 'name': '4- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],

    # 3. سكن خاص + تعديل واضافة
    'res_add':[
        {'code': 'ra_1_1', 'name': '1- دراسة المخطط الإنشائي القديم', 'stage': 'المرحلة الأولى', 'role': 'structural_id'},
        {'code': 'ra_1_2', 'name': '2- كشف على العقار', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'ra_1_3', 'name': '3- كروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'ra_1_4', 'name': '4- جمع الوثائق والمستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'ra_1_5', 'name': '5- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},

        {'code': 'ra_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'ra_2_2', 'name': '2- رسم البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},

        {'code': 'ra_3_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'ra_3_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'ra_3_3', 'name': '3- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},

        {'code': 'ra_4_1', 'name': '1- مخطط إنشائي كامل', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'ra_4_2', 'name': '2- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},

        {'code': 'ra_5_1', 'name': '1- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'ra_5_2', 'name': '2- كتب البنك', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
        {'code': 'ra_5_3', 'name': '3- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],

    # 4. غير سكني (استثماري، صناعي، إلخ) + تعديل واضافة
    'non_res_add':[
        {'code': 'nra_1_1', 'name': '1- دراسة المخطط الإنشائي القديم', 'stage': 'المرحلة الأولى', 'role': 'structural_id'},
        {'code': 'nra_1_2', 'name': '2- كشف على العقار', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'nra_1_3', 'name': '3- كروكي', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        {'code': 'nra_1_4', 'name': '4- جمع الوثائق والمستندات', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'nra_1_5', 'name': '5- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},

        {'code': 'nra_2_1', 'name': '1- سيستم الأعمدة', 'stage': 'المرحلة الثانية', 'role': 'structural_id'},
        {'code': 'nra_2_2', 'name': '2- رسم البلدية', 'stage': 'المرحلة الثانية', 'role': 'muni_draftsman_id'},

        {'code': 'nra_3_1', 'name': '1- إرسال للمطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_2', 'name': '2- اعتماد المطافي', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_3', 'name': '3- إرسال للتنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_4', 'name': '4- اعتماد التنظيم', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_5', 'name': '5- إرسال للبلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_6', 'name': '6- اعتماد البلدية', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
        {'code': 'nra_3_7', 'name': '7- تحصيل الدفعة الأخيرة من العقد', 'stage': 'المرحلة الثالثة', 'role': 'accountant_id'},

        {'code': 'nra_4_1', 'name': '1- مخطط إنشائي كامل', 'stage': 'المرحلة الرابعة', 'role': 'structural_id'},
        {'code': 'nra_4_2', 'name': '2- تجهيز الكراسة النهائية', 'stage': 'المرحلة الرابعة', 'role': 'secretary_id'},

        {'code': 'nra_5_1', 'name': '1- الإشراف على التنفيذ', 'stage': 'المرحلة الخامسة', 'role': 'structural_id'},
        {'code': 'nra_5_2', 'name': '3- إنهاء الإشراف', 'stage': 'المرحلة الخامسة', 'role': 'secretary_id'},
    ],
    
    # 5. هدم (لكل أنواع المباني) NEW WORKFLOW ADDED
    'demolition':[
        {'code': 'dem_1_1', 'name': '1- تجميع المستندات والوثائق', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'dem_1_2', 'name': '2- العقد وتحصيل الدفعة الأولى', 'stage': 'المرحلة الأولى', 'role': 'accountant_id'},
        {'code': 'dem_1_3', 'name': '3- توقيع نماذج البلدية', 'stage': 'المرحلة الأولى', 'role': 'secretary_id'},
        {'code': 'dem_1_4', 'name': '4- كتاب المواصفات وكتاب قطع تربة', 'stage': 'المرحلة الأولى', 'role': 'architect_id'},
        
        {'code': 'dem_2_1', 'name': '1- إرسال للبلدية', 'stage': 'المرحلة الثانية', 'role': 'secretary_id'},
        {'code': 'dem_2_2', 'name': '2- اعتماد البلدية', 'stage': 'المرحلة الثانية', 'role': 'secretary_id'},
        
        {'code': 'dem_3_1', 'name': '1- الإشراف على الهدم', 'stage': 'المرحلة الثالثة', 'role': 'structural_id'},
        {'code': 'dem_3_2', 'name': '2- إنهاء الإشراف', 'stage': 'المرحلة الثالثة', 'role': 'secretary_id'},
    ]
}

# ==============================================================================
#  SALE ORDER MODEL
# ==============================================================================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")

    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الضاحيه")
    area = fields.Char(string="مساحة الارض")
    
    governorate_id = fields.Many2one('kuwait.governorate', string="المحافظة")
    region_id = fields.Many2one('kuwait.region', string="المنطقة")

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
            elif order.service_type in['modification', 'addition', 'addition_modification']:
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
            'governorate_id': self.governorate_id.id,
            'region_id': self.region_id.id,
        }
        project = self.env['project.project'].create(project_vals)

        stages_to_create =['المرحلة الأولى', 'المرحلة الثانية', 'المرحلة الثالثة', 'المرحلة الرابعة', 'المرحلة الخامسة']

        for index, stage_name in enumerate(stages_to_create):
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
            'invoice_line_ids':[(0, 0, {'product_id': product_fee.id, 'quantity': 1, 'price_unit': 50.0, 'name': 'رسوم فتح ملف وتصميم مبدئي'})],
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


# ==============================================================================
#  PROJECT MODEL
# ==============================================================================
class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Source Quotation', readonly=True)
    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع المبنى")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")

    governorate_id = fields.Many2one('kuwait.governorate', string="المحافظة")
    region_id = fields.Many2one('kuwait.region', string="المنطقة")

    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الضاحيه")
    area = fields.Char(string="المساحة (Area)")

    architect_id = fields.Many2one('res.users', string="المهندس المعماري")
    accountant_id = fields.Many2one('res.users', string="المحاسبة")
    structural_id = fields.Many2one('res.users', string="المهندس الإنشائي")
    facade_draftsman_id = fields.Many2one('res.users', string="رسام الواجهات")
    secretary_id = fields.Many2one('res.users', string="السكرتارية")
    muni_draftsman_id = fields.Many2one('res.users', string="رسام البلدية")
    electrical_id = fields.Many2one('res.users', string="مهندس الكهرباء")
    draftsman_id = fields.Many2one('res.users', string="الرسام (صحي/مخططات)")

    workflow_started = fields.Boolean(default=False)
    triggered_steps = fields.Text(string="المهام المنفذة", default="")

    def _get_project_stages_map(self):
        self.ensure_one()
        stages = self.env['project.task.type'].search([('project_ids', 'in', self.id)], order='sequence')
        return {stage.name: stage.id for stage in stages}

    def _get_workflow_key(self):
        self.ensure_one()
        # 1. Check for Demolition First
        if self.service_type == 'demolition':
            return 'demolition'
            
        # 2. Check for Others
        is_addition = self.service_type in ['addition', 'modification', 'addition_modification']
        if self.building_type == 'residential':
            return 'res_add' if is_addition else 'res_new'
        else:
            return 'non_res_add' if is_addition else 'non_res_new'

    def action_start_workflow(self):
        self.ensure_one()
        if self.workflow_started:
            raise UserError(_("تم بدء سير العمل مسبقاً!"))

        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key,[])
        if not workflow:
            raise UserError(_("لا توجد خطة مهام مطابقة لنوع الخدمة والمبنى."))

        first_step = workflow[0]
        self._create_task_for_step(first_step)

        self.workflow_started = True
        self.triggered_steps = first_step['code'] + ","

    def _trigger_next_workflow_step(self, completed_code):
        self.ensure_one()
        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key,[])

        triggered = self.triggered_steps or ""

        for i, step in enumerate(workflow):
            if step['code'] == completed_code:
                if i + 1 < len(workflow):
                    next_step = workflow[i + 1]
                    if next_step['code'] not in triggered:
                        self._create_task_for_step(next_step)
                        self.triggered_steps = triggered + next_step['code'] + ","
                break

    def _create_task_for_step(self, step_data):
        stages_map = self._get_project_stages_map()
        stage_id = stages_map.get(step_data['stage'])
        if not stage_id:
            return

        # --- FIX: Calculate task Sequence to force 1, 2, 3, 4 sorting from Top to Bottom ---
        wf_key = self._get_workflow_key()
        workflow = WORKFLOW_TEMPLATES.get(wf_key, [])
        tasks_in_current_stage =[t for t in workflow if t['stage'] == step_data['stage']]
        
        task_sequence = 10
        for index, t in enumerate(tasks_in_current_stage):
            if t['code'] == step_data['code']:
                task_sequence = index + 1 # gives sequence 1, 2, 3, 4 to keep order correct.
                break
        # ----------------------------------------------------------------------------------

        user_id = getattr(self, step_data['role']).id if hasattr(self, step_data['role']) and getattr(self, step_data['role']) else False

        val = {
            'name': step_data['name'],
            'project_id': self.id,
            'stage_id': stage_id,
            'workflow_step': step_data['code'],
            'sequence': task_sequence # This forces Odoo Kanban to place 1 at the top
        }
        if user_id:
            val['user_ids'] = [(4, user_id)]

        self.env['project.task'].create(val)


# ==============================================================================
#  PROJECT TASK MODEL
# ==============================================================================
class ProjectTask(models.Model):
    _inherit = 'project.task'

    workflow_step = fields.Char(string="Workflow Trigger", readonly=True)
    phase_ids = fields.One2many('project.task.phase', 'task_id', string='مراحل التنفيذ (Phases)')

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        done_stage_id = self.env.ref('project.project_stage_3', raise_if_not_found=False)
        
        if 'stage_id' in vals and done_stage_id and vals['stage_id'] == done_stage_id.id:
            for task in self:
                if task.workflow_step and task.project_id:
                    task.project_id._trigger_next_workflow_step(task.workflow_step)
        return res

    def action_view_parent_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

# ==============================================================================
#  GOVERNORATE AND REGION MODELS
# ==============================================================================
class KuwaitGovernorate(models.Model):
    _name = 'kuwait.governorate'
    _description = 'Kuwait Governorate'
    name = fields.Char(string='المحافظة', required=True)

class KuwaitRegion(models.Model):
    _name = 'kuwait.region'
    _description = 'Kuwait Region'
    name = fields.Char(string='المنطقة', required=True)
    governorate_id = fields.Many2one('kuwait.governorate', string="المحافظة", required=True)

class ProjectTaskPhase(models.Model):
    _name = 'project.task.phase'
    _description = 'Task Construction Phase Checklist'
    _order = 'sequence, id'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sequence = fields.Integer(string='التسلسل', default=10)
    floor_category = fields.Char(string='الدور (Floor)', required=True)
    name = fields.Char(string='المرحلة (Phase)', required=True)
    is_completed = fields.Boolean(string='تم (Completed)', default=False)
