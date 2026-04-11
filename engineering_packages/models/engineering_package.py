# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


# ─────────────────────────────────────────────
#  Arabic Number to Words Helper
# ─────────────────────────────────────────────
def number_to_arabic_words(number):
    number = int(number)  # ignore fils for now

    if number == 0:
        return 'صفر'

    ones = [
        '', 'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة',
        'عشرة', 'أحد عشر', 'اثنا عشر', 'ثلاثة عشر', 'أربعة عشر', 'خمسة عشر',
        'ستة عشر', 'سبعة عشر', 'ثمانية عشر', 'تسعة عشر'
    ]
    tens = ['', '', 'عشرون', 'ثلاثون', 'أربعون', 'خمسون', 'ستون', 'سبعون', 'ثمانون', 'تسعون']
    hundreds = [
        '', 'مائة', 'مئتان', 'ثلاثمائة', 'أربعمائة', 'خمسمائة',
        'ستمائة', 'سبعمائة', 'ثمانمائة', 'تسعمائة'
    ]

    def _convert_below_1000(n):
        if n == 0:
            return ''
        elif n < 20:
            return ones[n]
        elif n < 100:
            ten = tens[n // 10]
            one = ones[n % 10]
            return (one + ' و' + ten) if one else ten
        else:
            h = hundreds[n // 100]
            rest = _convert_below_1000(n % 100)
            return (h + ' و' + rest) if rest else h

    result = ''

    if number >= 1000000:
        millions = number // 1000000
        if millions == 1:
            result += 'مليون '
        elif millions == 2:
            result += 'مليونان '
        else:
            result += _convert_below_1000(millions) + ' ملايين '
        number %= 1000000

    if number >= 1000:
        thousands = number // 1000
        if thousands == 1:
            result += 'ألف '
        elif thousands == 2:
            result += 'ألفان '
        elif 3 <= thousands <= 10:
            result += _convert_below_1000(thousands) + ' آلاف '
        else:
            result += _convert_below_1000(thousands) + ' ألف '
        number %= 1000

    if number > 0:
        result += _convert_below_1000(number)

    return result.strip()


# ─────────────────────────────────────────────
#  Models
# ─────────────────────────────────────────────
class EngineeringPackage(models.Model):
    _name = 'engineering.package'
    _description = 'Engineering Service Package'
    _order = 'sequence, name'

    name = fields.Char(string='اسم الباقة (Package Name)', required=True, translate=True)
    code = fields.Char(string='الرمز (Code)', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    package_type = fields.Selection([
        ('basic', 'الباقة الأساسية (Basic Package)'),
        ('premium', 'الباقة المميزة (Premium Package)'),
        ('gold', 'الباقة الذهبية (Gold Package)'),
        ('supervision', 'باقة الإشراف (Supervision Package)'),
        ('custom', 'باقة مخصصة (Custom Package)'),
    ], string="نوع الباقة (Package Type)", required=True, default='basic')

    building_type = fields.Selection([
        ('residential', 'سكن خاص (Private Housing)'),
        ('investment', 'استثماري (Investment Building)'),
        ('commercial', 'تجاري (Commercial Building)'),
        ('industrial', 'صناعي (Industrial Building)'),
        ('all', 'جميع الأنواع (All Types)'),
    ], string="نوع المبنى (Building Type)", default='all')

    service_type = fields.Selection([
        ('new_construction', 'بناء جديد (New Construction)'),
        ('demolition', 'هدم (Demolition)'),
        ('modification', 'تعديل (Modification)'),
        ('addition', 'اضافة (Addition)'),
        ('addition_modification', 'تعديل واضافة (Addition & Modification)'),
        ('supervision_only', 'إشراف هندسي فقط (Supervision Only)'),
        ('renovation', 'ترميم (Renovation)'),
        ('internal_partitions', 'قواطع داخلية (Internal Partitions)'),
        ('shades_garden', 'مظلات / حدائق (Shades / Garden)'),
        ('all', 'جميع الأنواع (All Types)')
    ], string="نوع الخدمة (Service Type)", default='all')

    description = fields.Html(string='الوصف (Description)')

    list_price = fields.Monetary(string='السعر (Price)', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id)

    product_line_ids = fields.One2many('engineering.package.line', 'package_id',
                                        string='منتجات الباقة (Package Products)')

    product_id = fields.Many2one('product.product', string='المنتج المرتبط (Related Product)',
                                  domain=[('is_engineering_package', '=', True)])

    feature_ids = fields.One2many('engineering.package.feature', 'package_id',
                                   string='مميزات الباقة (Package Features)')

    @api.depends('list_price')
    def _compute_price_in_arabic_words(self):
        for rec in self:
            rec.price_in_arabic_words = number_to_arabic_words(rec.list_price)

    price_in_arabic_words = fields.Char(
        string="السعر بالحروف العربية",
        compute=_compute_price_in_arabic_words,
        store=True, # You can store it if performance is a concern, but it's not strictly necessary for reports.
    )

    def action_create_product(self):
        self.ensure_one()
        if self.product_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'view_mode': 'form',
            }

        category = self.env['product.category'].search([('name', '=', 'الباقات الهندسية')], limit=1)
        if not category:
            category = self.env['product.category'].create({'name': 'الباقات الهندسية'})

        product = self.env['product.product'].create({
            'name': self.name,
            'default_code': self.code,
            'type': 'service',
            'list_price': self.list_price,
            'categ_id': category.id,
            'is_engineering_package': True,
            'engineering_package_id': self.id,
            'description_sale': self.description,
        })
        self.product_id = product
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': product.id,
            'view_mode': 'form',
        }


class EngineeringPackageLine(models.Model):
    _name = 'engineering.package.line'
    _description = 'Engineering Package Product Line'
    _order = 'sequence'

    package_id = fields.Many2one('engineering.package', string='الباقة', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='المنتج (Product)', required=True)
    quantity = fields.Float(string='الكمية (Quantity)', default=1.0)
    sequence = fields.Integer(default=10)

    product_uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='الوحدة')
    price_unit = fields.Float(related='product_id.list_price', string='سعر الوحدة')
    subtotal = fields.Float(compute='_compute_subtotal', string='المجموع')

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit


class EngineeringPackageFeature(models.Model):
    _name = 'engineering.package.feature'
    _description = 'Engineering Package Feature'
    _order = 'sequence'

    package_id = fields.Many2one('engineering.package', string='الباقة', ondelete='cascade')
    name = fields.Char(string='الميزة (Feature)', required=True)
    included = fields.Boolean(string='مشمولة (Included)', default=True)
    sequence = fields.Integer(default=10)


# ─────────────────────────────────────────────
#  Sale Order Inherit — adds amount_in_arabic_words()
# ─────────────────────────────────────────────
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def amount_in_arabic_words(self):
        self.ensure_one()
        # This function currently uses amount_total.
        # If you intend to use it for package price, you'd need to adapt it.
        # For now, we'll use the new computed field on engineering.package directly.
        return number_to_arabic_words(self.amount_total)