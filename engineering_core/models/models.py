# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import urllib.parse

# Helper function to get the list of areas organized by governorate
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
            ('جزيرة قارووه', 'جزيرة قارووه'), ('جزيرة كبر', 'جزيرة ككبر'),
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

def _get_dynamic_regions_selection(self):
    current_governorate = self.governorate
    if current_governorate:
        return _get_governorate_areas().get(current_governorate, [])
    return []

# ==============================================================================
#  RES PARTNER
# ==============================================================================
class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار", tracking=True)
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة", tracking=True)
    civil_number = fields.Char(string="الرقم المدني (Civil ID)")
    plot_no = fields.Char(string="رقم القسيمة (Plot)")
    block_no = fields.Char(string="القطعة (Block)")
    street_no = fields.Char(string="الشارع (Street)")
    area = fields.Char(string="مساحة الارض (Area)")
    
    governorate = fields.Selection(
        selection=[(gov, gov) for gov in _get_governorate_areas().keys()],
        string="المحافظة (Governorate)", tracking=True
    )
    region = fields.Selection(_get_dynamic_regions_selection, string="المنطقة (Region)", tracking=True)

    # Odoo 17: New computed fields for dynamic UI
    region_is_visible = fields.Boolean(compute='_compute_region_properties')
    region_is_required = fields.Boolean(compute='_compute_region_properties')

    @api.depends('governorate')
    def _compute_region_properties(self):
        for record in self:
            record.region_is_visible = bool(record.governorate)
            record.region_is_required = bool(record.governorate)


    @api.onchange('governorate')
    def _onchange_governorate(self):
        self.region = False
        if self.governorate:
            return {'domain': {'region': _get_governorate_areas().get(self.governorate, [])}}
        return {'domain': {'region': []}}
        
    @api.constrains('governorate', 'region')
    def _check_valid_region(self):
        for record in self:
            if record.governorate and record.region:
                valid_regions = [area[0] for area in _get_governorate_areas().get(record.governorate, [])]
                if record.region not in valid_regions:
                    raise ValidationError(_("المنطقة المختارة '%s' لا تتبع للمحافظة '%s'.") % (record.region, record.governorate))


# ==============================================================================
#  CRM LEAD
# ==============================================================================
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")
    plot_no = fields.Char(string="رقم القسيمة (Plot)")
    block_no = fields.Char(string="القطعة (Block)")
    street_no = fields.Char(string="الشارع (Street)")
    area = fields.Char(string="مساحة الارض (Area)")
    
    governorate = fields.Selection(
        selection=[(gov, gov) for gov in _get_governorate_areas().keys()],
        string="المحافظة (Governorate)"
    )
    region = fields.Selection(_get_dynamic_regions_selection, string="المنطقة (Region)")

    # Odoo 17: New computed fields for dynamic UI
    region_is_visible = fields.Boolean(compute='_compute_region_properties')
    region_is_required = fields.Boolean(compute='_compute_region_properties')

    @api.depends('governorate')
    def _compute_region_properties(self):
        for record in self:
            record.region_is_visible = bool(record.governorate)
            record.region_is_required = bool(record.governorate)

    @api.onchange('governorate')
    def _onchange_governorate(self):
        self.region = False
        if self.governorate:
            return {'domain': {'region': _get_governorate_areas().get(self.governorate, [])}}
        return {'domain': {'region': []}}
    
    @api.constrains('governorate', 'region')
    def _check_valid_region(self):
        for record in self:
            if record.governorate and record.region:
                valid_regions = [area[0] for area in _get_governorate_areas().get(record.governorate, [])]
                if record.region not in valid_regions:
                    raise ValidationError(_("المنطقة المختارة '%s' لا تتبع للمحافظة '%s'.") % (record.region, record.governorate))
    
    def _prepare_sale_order_values(self, partner, company, access_token):
        values = super()._prepare_sale_order_values(partner, company, access_token)
        values['building_type'] = self.building_type
        values['service_type'] = self.service_type
        values['plot_no'] = self.plot_no
        values['block_no'] = self.block_no
        values['street_no'] = self.street_no
        values['area'] = self.area
        values['governorate'] = self.governorate
        values['region'] = self.region
        return values


# ==============================================================================
#  SALE ORDER (Keep this section for context, assuming it's in the same file)
# ==============================================================================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار", store=True)
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة", store=True)

    plot_no = fields.Char(string="رقم القسيمة", store=True)
    block_no = fields.Char(string="القطعة", store=True)
    street_no = fields.Char(string="الشارع", store=True)
    area = fields.Char(string="مساحة الارض", store=True)
    
    governorate = fields.Selection(
        selection=[(gov, gov) for gov in _get_governorate_areas().keys()],
        string="المحافظة (Governorate)", store=True
    )
    region = fields.Selection(_get_dynamic_regions_selection, string="المنطقة (Region)", store=True)

    # Odoo 17: New computed fields for dynamic UI
    region_is_visible = fields.Boolean(compute='_compute_region_properties')
    region_is_required = fields.Boolean(compute='_compute_region_properties')

    @api.depends('governorate')
    def _compute_region_properties(self):
        for record in self:
            record.region_is_visible = bool(record.governorate)
            record.region_is_required = bool(record.governorate)

    @api.onchange('governorate')
    def _onchange_governorate(self):
        self.region = False
        if self.governorate:
            return {'domain': {'region': _get_governorate_areas().get(self.governorate, [])}}
        return {'domain': {'region': []}}
        
    @api.constrains('governorate', 'region')
    def _check_valid_region(self):
        for record in self:
            if record.governorate and record.region:
                valid_regions = [area[0] for area in _get_governorate_areas().get(record.governorate, [])]
                if record.region not in valid_regions:
                    raise ValidationError(_("المنطقة المختارة '%s' لا تتبع للمحافظة '%s'.") % (record.region, record.governorate))

# ... (Include other classes like ProjectProject and ProjectTask if they are in this file,
#      applying the same region_is_visible/required pattern if needed there too.)

# The ProjectProject and ProjectTask classes (and any other classes) from your original code
# would go here, continuing to use _get_dynamic_regions_selection for their 'region' fields
# and implementing the onchange and constrains methods as well.

# Example for ProjectProject (if you have it in this file as well):
class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Quotation Source', readonly=True)
    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('addition', 'اضافة'), ('addition_modification', 'تعديل واضافة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")
    
    governorate = fields.Selection(
        selection=[(gov, gov) for gov in _get_governorate_areas().keys()],
        string="المحافظة"
    )

    # Use the dynamic selection helper here too
    region = fields.Selection(
        selection=_get_dynamic_regions_selection,
        string="المنطقة"
    )
    
    @api.onchange('governorate')
    def _onchange_governorate(self):
        self.region = False
        if self.governorate:
            return {'domain': {'region': _get_governorate_areas().get(self.governorate, [])}}
        return {'domain': {'region': []}}
        
    @api.constrains('governorate', 'region')
    def _check_valid_region(self):
        for project in self:
            if project.governorate and project.region:
                valid_regions = [area[0] for area in _get_governorate_areas().get(project.governorate, [])]
                if project.region not in valid_regions:
                    raise ValidationError(_("المنطقة المختارة '%s' لا تتبع للمحافظة '%s'.") % (project.region, project.governorate))

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
