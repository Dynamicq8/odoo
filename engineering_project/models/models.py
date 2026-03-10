# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import urllib.parse

# ==============================================================================
#  HELPER FUNCTIONS FOR GOVERNORATE & REGION 
# ==============================================================================
def _get_governorate_areas():
    return {
        'محافظة العاصمة': [
            ('جابر الاحمد', 'جابر الاحمد'), ('القبلة', 'القبلة'), ('الشرق', 'الشرق'),
            ('المرقاب', 'المرقاب'), ('الصالحية', 'الصالحية'), ('دسمان', 'دسمان'),
            ('الدعية', 'الدعية'), ('الدسمة', 'الدسمة'), ('كيفان', 'كيفان'),
            ('الخالدية', 'الخالدية'), ('الشامية', 'الشامية'), ('الروضة', 'الروضة'),
            ('العديلية', 'العديلية'), ('الفيحاء', 'الفيحاء'), ('القادسية', 'القادسية'),
            ('قرطبة', 'قرطبة'), ('السرة', 'السرة'), ('اليرموك', 'اليرموك'),
            ('النزهة', 'النزهة'), ('الشويخ الصناعية 1', 'الشويخ الصناعية 1'),
            ('الشويخ الصناعية 2', 'الشويخ الصناعية 2'), ('الشويخ الصناعية 3', 'الشويخ الصناعية 3'),
            ('الشويخ الادارية', 'الشويخ الادارية'), ('الشويخ السكنى', 'الشويخ السكنى'),
            ('الشويخ التعليمية', 'الشويخ التعليمية'), ('الشويخ الصحيه', 'الشويخ الصحيه'),
            ('الواجهه البحرية', 'الواجهه البحرية'), ('غرناطة', 'غرناطة'),
            ('الصليبيخات', 'الصليبيخات'), ('المنصورية', 'المنصورية'),
            ('الدوحة السكنيه', 'الدوحة السكنيه'), ('الرى', 'الرى'),
            ('ميناء الدوحة', 'ميناء الدوحة'), ('جزيره عوهه', 'جزيره عوهه'),
            ('جزيره فيلكه', 'جزيره فيلكه'), ('جزيره مسكان', 'جزيره مسكان'),
            ('حدائق السور – الحزام الاخضر', 'حدائق السور – الحزام الاخضر'),
            ('بنيد القار', 'بنيد القار'), ('ميناء الشويخ', 'ميناء الشويخ'),
            ('معسكرات المباركيه – جيوان', 'معسكرات المباركيه – جيوان'),
            ('شاليهات الدوحة', 'شاليهات الدوحة'), ('السره', 'السره'),
        ],
        'محافظة حولي': [
            ('حولي', 'حولي'), ('السالمية', 'السالمية'), ('الرميثية', 'الرميثية'),
            ('الجابرية', 'الجابرية'), ('بيان', 'بيان'), ('مشرف', 'مشرف'),
            ('سلوى', 'سلوى'), ('ميدان حولي', 'ميدان حولي'), ('الزهراء', 'الزهراء'),
            ('الصديق', 'الصديق'), ('حطين', 'حطين'), ('السلام', 'السلام'),
            ('الشهداء', 'الشهداء'), ('انجفة', 'انجفة'), ('الشعب', 'الشعب'),
            ('مبارك العبد الله', 'مبارك العبد الله'), ('الواجهه البحريه', 'الواجهه البحريه'),
            ('الضاحيه الدبلوماسيه', 'الضاحيه الدبلوماسيه'),
            ('المباركيه قطعة 15 بيان', 'المباركيه قطعة 15 بيان'), ('البدع', 'البدع'),
        ],
        'محافظة الفروانية': [
            ('الفروانية', 'الفروانية'), ('خيطان', 'خيطان'), ('العمرية', 'العمرية'),
            ('الرحاب', 'الرحاب'), ('الرقعى', 'الرقعى'), ('الشدادية', 'الشدادية'),
            ('الضجيج', 'الضجيج'), ('المطار', 'المطار'),
            ('غرب الجليب الشداديه', 'غرب الجليب الشداديه'),
            ('عبد الله المبارك', 'عبد الله المبارك'),
            ('مدينه صباح السالم الجامعية', 'مدينه صباح السالم الجامعية'),
            ('منطقة المعارض جنوب خيطان', 'منطقة المعارض جنوب خيطان'),
            ('الأندلس', 'الأندلس'), ('إشبيلية', 'إشبيلية'),
            ('جليب الشيوخ', 'جليب الشيوخ'), ('الفردوس', 'الفردوس'),
            ('صباح الناصر', 'صباح الناصر'), ('الرابية', 'الرابية'),
            ('العارضية', 'العارضية'),
            ('العارضية استعمالات حكومية', 'العارضية استعمالات حكومية'),
            ('العارضية مخازن', 'العارضية مخازن'), ('العارضية الحرفية', 'العارضية الحرفية'),
            ('غرب عبد المبارك السكنى', 'غرب عبد المبارك السكنى'),
            ('جنوب عبد الله المبارك السكنى', 'جنوب عبد الله المبارك السكنى'),
            ('العباسية', 'العباسية'),
        ],
        'محافظة الأحمدي': [
            ('الأحمدي', 'الأحمدي'), ('الفحيحيل', 'الفحيحيل'), ('المنقف', 'المنقف'),
            ('أبو حليفة', 'أبو حليفة'), ('الصباحية', 'الصباحية'), ('الرقة', 'الرقة'),
            ('هدية', 'هدية'), ('الفنطاس', 'الفنطاس'), ('المهبولة', 'المهبولة'),
            ('العقيلة', 'العقيلة'), ('الظهر', 'الظهر'), ('جابر العلي', 'جابر العلي'),
            ('صباح الأحمد السكنية', 'صباح الأحمد السكنية'), ('الوفرة', 'الوفرة'),
            ('الخيران', 'الخيران'), ('ميناء الزور', 'ميناء الزور'),
            ('ميناء عبد الله الصناعية', 'ميناء عبد الله الصناعية'),
            ('ميناء عبد الله', 'ميناء عبد الله'), ('مزارع الوفره', 'مزارع الوفره'),
            ('صباح الاحمد السكنيه', 'صباح الاحمد السكنيه'),
            ('صباح الاحمد البحريه', 'صباح الاحمد البحريه'),
            ('قردان والحفيرة والفوار', 'قردان والحفيرة والفوار'),
            ('فهد الاحمد', 'فهد الاحمد'),
            ('على صباح السالم – ام الهيمان', 'على صباح السالم – ام الهيمان'),
            ('عريفجان', 'عريفجان'), ('ضليع الزنيف', 'ضليع الزنيف'),
            ('شرق الاحمدى الخدميه والحرفية والتجاريه', 'شرق الاحمدى الخدميه والحرفية والتجاريه'),
            ('شرق الاحمدى', 'شرق الاحمدى'),
            ('شاليهات ميناء عبد الله', 'شاليهات ميناء عبد الله'),
            ('شاليهات بنيدر', 'شاليهات بنيدر'),
            ('شاليهات النويصيب', 'شاليهات النويصيب'),
            ('شاليهات الضاعيه', 'شاليهات الضاعيه'), ('شاليهات الزور', 'شاليهات الزور'),
            ('شاليهات الخيران', 'شاليهات الخيران'),
            ('شاليهات الجليعه', 'شاليهات الجليعه'),
            ('رجم خشمان ومصلان', 'رجم خشمان ومصلان'),
            ('جنوب الصباحية', 'جنوب الصباحية'), ('برقان', 'برقان'),
            ('الوفره السكنيه', 'الوفره السكنيه'),
            ('الهيئة العامة للزراعة والثورة السمكيه – مزارع', 'الهيئة العامة للزراعة والثورة السمكيه – مزارع'),
            ('النويصيب', 'النويصيب'), ('المقوع', 'المقوع'), ('الفحيحيل', 'الفحيحيل'),
            ('العبدليه', 'العبدليه'),
            ('الصناعية الصناعية الخلط الجاهز', 'الصناعية الصناعية الخلط الجاهز'),
            ('الشعيبة الصناعية الشرقيه', 'الشعيبة الصناعية الشرقيه'),
            ('الشعيبة الصناعية الغربيه', 'الشعيبة الصناعية الغربيه'),
            ('الشعيبة', 'الشعيبة'), ('الشدادية الصناعية', 'الشدادية الصناعية'),
            ('الزور وصوله', 'الزور وصوله'), ('ام حجول', 'ام حجول'),
            ('ام قدير', 'ام قدير'), ('ابو خرجين والصبيحية', 'ابو خرجين والصبيحية'),
        ],
        'محافظة الجهراء': [
            ('الجهراء', 'الجهراء'), ('القصر', 'القصر'), ('النسيم', 'النسيم'),
            ('الواحة', 'الواحة'), ('النعيم', 'النعيم'), ('تيماء', 'تيماء'),
            ('سعد العبدالله', 'سعد العبدالله'), ('الصليبية', 'الصليبية'),
            ('كبد', 'كبد'), ('المطلاع', 'المطلاع'), ('أمغرة', 'أمغرة'),
            ('البحيث', 'البحيث'), ('الجهراء الصناعية الثانية', 'الجهراء الصناعية الثانية'),
            ('الجهراء الصناعية الحرفيه الاولى', 'الجهراء الصناعية الحرفيه الاولى'),
            ('الرتقة والحريجه', 'الرتقة والحريجه'),
            ('الرحية وام توينج', 'الرحية وام توينج'), ('الروضتين', 'الروضتين'),
            ('السالمى', 'السالمى'), ('السكراب', 'السكراب'),
            ('الشقايا – الدبدبة – المتياهه', 'الشقايا – الدبدبة – المتياهه'),
            ('الصابرية – العرفجية', 'الصابرية – العرفجية'),
            ('الصبية', 'الصبية'), ('الصليبية الزراعية', 'الصليبية الزراعية'),
            ('الصليبيه السكنية', 'الصليبيه السكنية'),
            ('الصليبية الصناعية 2', 'الصليبية الصناعية 2'),
            ('الصليبيه الصناعية 1', 'الصليبيه الصناعية 1'),
            ('الصير وام المدفاع', 'الصير وام المدفاع'), ('العبدلى', 'العبدلى'),
            ('العبدلى وصخيبريات', 'العبدلى وصخيبريات'), ('العيون', 'العيون'),
            ('القيروان – جنوب الدوحة', 'القيروان – جنوب الدوحة'),
            ('المستثمر الاجنبى (منطقة العبدلى الاقتصادية )', 'المستثمر الاجنبى (منطقة العبدلى الاقتصادية )'),
            ('المطلاع وجال الاطراف', 'المطلاع وجال الاطراف'),
            ('النعايم الصناعية', 'النعايم الصناعية'),
            ('النهضة – شرق الصليبخات', 'النهضة – شرق الصليبخات'),
            ('امغره الصناعية', 'امغره الصناعية'), ('تيماء', 'تيماء'),
            ('جال الزور', 'جال الزور'), ('جزيرة ام المرادم', 'جزيرة ام المرادم'),
            ('جزيره ام النمل', 'جزيره ام النمل'), ('جزيرة بوبيان', 'جزيرة بوبيان'),
            ('جزيرة قارووه', 'جزيرة قارووه'), ('جزيرة كبر', 'جزيرة كبر'),
            ('جزيرة وربة', 'جزيرة وربة'), ('جنوب امغرة', 'جنوب امغرة'),
            ('شرق الجهراء', 'شرق الجهراء'), ('شرق تيماء', 'شرق تيماء'),
            ('شمال غرب الجهراء', 'شمال غرب الجهراء'),
            ('قلمة شايع والمناقيش', 'قلمة شايع والمناقيش'),
            ('كاظمة', 'كاظمة'), ('كبد والشق والضبعة', 'كبد والشق والضبعة'),
            ('معسكرات الجهراء', 'معسكرات الجهراء'), ('مقبرة', 'مقبرة'),
            ('مناطق نائية -الجهراء', 'مناطق نائية -الجهراء'),
        ],
        'محافظة مبارك الكبير': [
            ('مبارك الكبير', 'مبارك الكبير'), ('العدان', 'العدان'),
            ('القرين', 'القرين'), ('القصور', 'القصور'), ('المسيلة', 'المسيلة'),
            ('غرب أبو فطيرة', 'غرب أبو فطيرة'), ('الفنيطيس', 'الفنيطيس'),
            ('المسايل', 'المسايل'), ('الوسطى', 'الوسطى'),
            ('جنوب الوسطى', 'جنوب الوسطى'), ('صباح السالم', 'صباح السالم'),
            ('صبحان الصناعية', 'صبحان الصناعية'),
            ('ضاحية ابو فطيرة', 'ضاحية ابو فطيرة'), ('ابو الحصانية', 'ابو الحصانية'),
        ],
    }

def _get_all_regions(self):
    all_regions = []
    seen_regions = set()
    for areas in _get_governorate_areas().values():
        for area_val, area_label in areas:
            if area_val not in seen_regions:
                all_regions.append((area_val, area_label))
                seen_regions.add(area_val)
    return sorted(all_regions, key=lambda x: x[1])


# ==============================================================================
#  SALE ORDER MODEL 
# ==============================================================================
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
            'governorate_id': self.governorate_id.id, 
            'region_id': self.region_id.id,
        }
        project = self.env['project.project'].create(project_vals)
        
        if self.building_type == 'residential': 
            stages_to_create = [
                'التصميم المبدئي', 
                'التعاقد والوثائق', 
                'سيستم الأعمدة', 
                'الواجهات', 
                'رسوم البلدية', 
                'مرحلة التراخيص', 
                'مخطط إنشائي', 
                'مخططات تفصيلية', 
                'الإشراف'
            ]
        else: 
            stages_to_create = [
                'التصميم المبدئي', 
                'التعاقد والوثائق', 
                'المخطط الانشائي', 
                'الموافقات', 
                'التصميمات التفصيلية', 
                'الإشراف', 
                'إنهاء المشروع'
            ]

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
    
    @api.onchange('governorate_id')
    def _onchange_governorate(self):
        self.region_id = False
        
    @api.constrains('governorate_id', 'region_id')
    def _check_valid_region(self):
        for project in self:
            gov_name = project.governorate_id.name if project.governorate_id else False
            region_name = project.region_id.name if project.region_id else False
            if gov_name and region_name:
                valid_regions = [area[0] for area in _get_governorate_areas().get(gov_name, [])]
                if region_name not in valid_regions:
                    raise ValidationError(_("المنطقة المختارة '%s' لا تتبع للمحافظة '%s'.") % (region_name, gov_name))

    plot_no = fields.Char(string="رقم القسيمة")
    block_no = fields.Char(string="القطعة")
    street_no = fields.Char(string="الشارع")
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
    residential_step_1_triggered = fields.Boolean(default=False)
    residential_step_2_triggered = fields.Boolean(default=False)
    residential_step_3_triggered = fields.Boolean(default=False)
    residential_step_4_triggered = fields.Boolean(default=False)
    residential_step_5_triggered = fields.Boolean(default=False)
    residential_step_6_triggered = fields.Boolean(default=False)
    residential_step_7_triggered = fields.Boolean(default=False)
    residential_step_8_triggered = fields.Boolean(default=False)
    step_2_triggered = fields.Boolean(default=False)
    step_3_triggered = fields.Boolean(default=False)
    step_4_triggered = fields.Boolean(default=False)
    step_5_triggered = fields.Boolean(default=False)
    step_6_triggered = fields.Boolean(default=False)
    step_8_triggered = fields.Boolean(default=False)
    step_9_triggered = fields.Boolean(default=False)
    step_10_triggered = fields.Boolean(default=False)


    def _get_project_stages_map(self):
        self.ensure_one()
        stages = self.env['project.task.type'].search([('project_ids', 'in', self.id)], order='sequence')
        return {stage.name: stage.id for stage in stages}


    def action_start_workflow(self):
        self.ensure_one()
        if self.workflow_started:
            raise UserError(_("تم بدء سير العمل مسبقاً!"))
        
        stages_map = self._get_project_stages_map()

        if self.building_type == 'residential':
            s_initial_design = stages_map.get('التصميم المبدئي')
            self._create_task('1. كروكي', self.architect_id, s_initial_design, 'residential_task_1')
            self._create_task('1. مباني أولية', self.architect_id, s_initial_design)
        else:
            s0 = stages_map.get('التصميم المبدئي')
            self._create_task('1. كروكي معماري', self.architect_id, s0, 'step_1')
            
        self.workflow_started = True

    def _trigger_next_workflow_step(self, completed_step):
        self.ensure_one()
        stages_map = self._get_project_stages_map()

        if self.building_type == 'residential':
            s_initial_design = stages_map.get('التصميم المبدئي')
            s_contract_docs = stages_map.get('التعاقد والوثائق')
            s_column_system = stages_map.get('سيستم الأعمدة')
            s_facades = stages_map.get('الواجهات')
            s_muni_fees = stages_map.get('رسوم البلدية')
            s_licensing = stages_map.get('مرحلة التراخيص')
            s_structural_plan = stages_map.get('مخطط إنشائي')
            s_detailed_plans = stages_map.get('مخططات تفصيلية')
            s_supervision = stages_map.get('الإشراف')

            if completed_step == 'residential_task_1' and not self.residential_step_1_triggered:
                self._create_task('2. العقد وتحصيل الدفعة الأولى', self.accountant_id, s_contract_docs, 'residential_task_2')
                self._create_task('2. جمع الوثائق', self.secretary_id, s_contract_docs)
                self.residential_step_1_triggered = True

            elif completed_step == 'residential_task_2' and not self.residential_step_3_triggered:
                self._create_task('3. سيستم الأعمدة', self.structural_id, s_column_system, 'residential_task_3')
                self._create_task('3. 3D ELEVATION', self.facade_draftsman_id, s_facades) 
                self.residential_step_3_triggered = True

            elif completed_step == 'residential_task_3' and not self.residential_step_4_triggered:
                self._create_task('4. 2D ELEVATION', self.facade_draftsman_id, s_facades, 'residential_task_4') 
                self.residential_step_4_triggered = True

            elif completed_step == 'residential_task_4' and not self.residential_step_5_triggered:
                self._create_task('5. رسم مخطط البلدية', self.muni_draftsman_id, s_muni_fees, 'residential_task_5')
                self.residential_step_5_triggered = True

            elif completed_step == 'residential_task_5' and not self.residential_step_6_triggered:
                self._create_task('6. موافقة البلدية', self.secretary_id, s_licensing, 'residential_task_6_muni_approve')
                self._create_task('6. ادارية انهاءية', self.secretary_id, s_licensing, 'residential_task_6_admin_finish') 
                self.residential_step_6_triggered = True
            
            elif completed_step == 'residential_task_6_muni_approve' and self.residential_step_6_triggered and not self.residential_step_7_triggered:
                self._create_task('7. انشائي تفصيلي', self.structural_id, s_structural_plan, 'residential_task_7')
                self.residential_step_7_triggered = True

            elif completed_step == 'residential_task_7' and not self.residential_step_8_triggered:
                self._create_task('8. مخطط صحي', self.draftsman_id, s_detailed_plans)
                self._create_task('8. مخطط كهربائي', self.electrical_id, s_detailed_plans)
                self._create_task('8. كشف الكميات', self.accountant_id, s_detailed_plans)
                self._create_task('8. انهاء المباني', self.architect_id, s_detailed_plans)
                self._create_task('8. عقود اشراف', self.secretary_id, s_supervision, 'residential_task_8')
                self.residential_step_8_triggered = True
            
            elif completed_step == 'residential_task_8':
                self._create_task('9. اعمال الاشراف', self.structural_id, s_supervision)

        else:
            s0 = stages_map.get('التصميم المبدئي')
            s1 = stages_map.get('التعاقد والوثائق')
            s2 = stages_map.get('المخطط الانشائي')
            s3 = stages_map.get('الموافقات')
            s4 = stages_map.get('التصميمات التفصيلية')
            s5 = stages_map.get('الإشراف')
            s6 = stages_map.get('إنهاء المشروع')

            if completed_step == 'step_1' and not self.step_2_triggered:
                self._create_task('2. العقد وتحصيل الدفعة الاولي', self.accountant_id, s1)
                self._create_task('2. جمع الوثائق وتعبة النماذج', self.secretary_id, s1)
                self._create_task('2. سيستم الاعمدة', self.structural_id, s2, 'step_2_cols')
                self._create_task('2. الواجهات', self.facade_draftsman_id, s4)
                self.step_2_triggered = True

            elif completed_step == 'step_2_cols' and not self.step_3_triggered:
                self._create_task('3. رسم المعماري للبلدية', self.muni_draftsman_id, s3, 'step_3')
                self.step_3_triggered = True

            elif completed_step == 'step_3' and not self.step_4_triggered:
                self._create_task('4. ادخال المعاملة بلدية للاعتماد', self.secretary_id, s3, 'step_4')
                self.step_4_triggered = True

            elif completed_step == 'step_4' and not self.step_5_triggered:
                self._create_task('5. اعتماد الرخصة من البلدية', self.secretary_id, s3, 'step_5')
                self.step_5_triggered = True

            elif completed_step == 'step_5' and not self.step_6_triggered:
                self._create_task('6. تصميم الانشائي الكامل', self.structural_id, s4, 'step_6')
                self._create_task('7. تصميم مخطط الصحي', self.draftsman_id, s4)
                self._create_task('7. تصميم مخطط الكهرباء', self.electrical_id, s4)
                self.step_6_triggered = True

            elif completed_step == 'step_6' and not self.step_8_triggered:
                self._create_task('8. تعهد الاشراف', self.secretary_id, s5, 'step_8')
                self.step_8_triggered = True

            elif completed_step == 'step_8' and not self.step_9_triggered:
                self._create_task('9. الاشراف علي التنفيذ', self.structural_id, s5, 'step_9')
                self.step_9_triggered = True

            elif completed_step == 'step_9' and not self.step_10_triggered:
                self._create_task('10. انهاء الاشراف', self.secretary_id, s6)
                self.step_10_triggered = True

    def _create_task(self, name, user, stage_id, workflow_step=False):
        if not stage_id: return 
        val = {'name': name, 'project_id': self.id, 'stage_id': stage_id}
        if user: val['user_ids'] = [(4, user.id)]
        if workflow_step: val['workflow_step'] = workflow_step
        self.env['project.task'].create(val)


# ==============================================================================
#  PROJECT TASK MODEL - (FIXED: Fields added back!)
# ==============================================================================
class ProjectTask(models.Model):
    _inherit = 'project.task'

    # --- THIS WAS MISSING: The Workflow Trigger Field ---
    workflow_step = fields.Selection([
        ('step_1', 'Step 1'),
        ('step_2_cols', 'Step 2 Cols'),
        ('step_3', 'Step 3'),
        ('step_4', 'Step 4'),
        ('step_5', 'Step 5'),
        ('step_6', 'Step 6'),
        ('step_8', 'Step 8'),
        ('step_9', 'Step 9'),
        ('step_10', 'Step 10'),
        ('residential_task_1', 'Residential Task 1'),
        ('residential_task_2', 'Residential Task 2'),
        ('residential_task_3', 'Residential Task 3'),
        ('residential_task_4', 'Residential Task 4'),
        ('residential_task_5', 'Residential Task 5'),
        ('residential_task_6_muni_approve', 'Residential Task 6 Muni Approval'),
        ('residential_task_6_admin_finish', 'Residential Task 6 Admin Finish'),
        ('residential_task_7', 'Residential Task 7'),
        ('residential_task_8', 'Residential Task 8'),
    ], string="Workflow Trigger", readonly=True)

     phase_ids = fields.One2many('project.task.phase', 'task_id', string='مراحل التنفيذ (Phases)')

    def action_load_default_phases(self):
        """ Loads the default checklist based on building type """
        for task in self:
            if task.phase_ids:
                continue # Don't overwrite if they already loaded it

            seq = 10
            phases_data = [
                ('مرحله الحفر', 'عام (General)'),
                ('مرحله القواعد والشناجات', 'عام (General)'),
                ('مرحله حوائط السرداب', 'السرداب (Basement)'),
                ('مرحله صب سقف السرداب', 'السرداب (Basement)'),
                ('مرحله اعمده الدور الارضى', 'الدور الأرضي (Ground)'),
                ('مرحله صب سقف الدور الارضى', 'الدور الأرضي (Ground)'),
                ('مرحله اعمده الدور الاول', 'الدور الأول (First)'),
                ('مرحله صب سقف الدور الاول', 'الدور الأول (First)'),
                ('مرحله اعمده الدور الثانى', 'الدور الثاني (Second)'),
                ('مرحله صب سقف الدور الثانى', 'الدور الثاني (Second)'),
                ('مرحله اعمده الدور السطح', 'السطح (Roof)'),
                ('مرحله صب سقف السطح', 'السطح (Roof)'),
            ]

            phases_to_create = []
            for name, category in phases_data:
                phases_to_create.append((0, 0, {
                    'name': name,
                    'floor_category': category,
                    'sequence': seq
                }))
                seq += 10

            task.write({'phase_ids': phases_to_create})

    def get_completed_phases_grouped(self):
        """ Helper method for the PDF Report to group checked items by floor """
        self.ensure_one()
        completed_phases = self.phase_ids.filtered(lambda p: p.is_completed)
        
        # Group by floor_category while preserving order
        grouped = {}
        for phase in completed_phases:
            cat = phase.floor_category
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(phase)
        return grouped

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if 'state' in vals and vals['state'] in ['03_approved', '1_done']:
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

    def action_send_task_form_whatsapp(self):
        self.ensure_one()
        phone = self.project_id.partner_id.mobile or self.project_id.partner_id.phone
        if not phone: raise UserError("رقم الهاتف مفقود للعميل في المشروع")
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self._portal_ensure_token()
        project_url = f"{base_url}/report/pdf/engineering_project.report_initial_design_template/{self.id}"
        message = _("مرحباً %s،\nنرفق لكم نموذج مكونات المشروع للمراجعة.\nالرابط:\n%s") % (self.project_id.partner_id.name, project_url)
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"
        return { 'type': 'ir.actions.act_url', 'url': whatsapp_url, 'target': 'new' }

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
