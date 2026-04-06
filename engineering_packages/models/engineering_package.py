# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class EngineeringPackage(models.Model):
    _name = 'engineering.package'
    _description = 'Engineering Service Package'
    _order = 'sequence, name'

    name = fields.Char(string='اسم الباقة (Package Name)', required=True, translate=True)
    code = fields.Char(string='الرمز (Code)', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # Package Type
    package_type = fields.Selection([
        ('basic', 'الباقة الأساسية (Basic Package)'),
        ('premium', 'الباقة المميزة (Premium Package)'),
        ('gold', 'الباقة الذهبية (Gold Package)'),
        ('supervision', 'باقة الإشراف (Supervision Package)'),
        ('custom', 'باقة مخصصة (Custom Package)'),
    ], string="نوع الباقة (Package Type)", required=True, default='basic')

    # Building Type Applicability
    building_type = fields.Selection([
        ('residential', 'سكن خاص (Private Housing)'),
        ('investment', 'استثماري (Investment Building)'),
        ('commercial', 'تجاري (Commercial Building)'),
        ('industrial', 'صناعي (Industrial Building)'),
        ('all', 'جميع الأنواع (All Types)'),
    ], string="نوع المبنى (Building Type)", default='all')

    # Service Type Applicability
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

    # Package Description
    description = fields.Html(string='الوصف (Description)')
    
    # Package Price
    list_price = fields.Monetary(string='السعر (Price)', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                   default=lambda self: self.env.company.currency_id)

    # Bundle Products
    product_line_ids = fields.One2many('engineering.package.line', 'package_id', 
                                        string='منتجات الباقة (Package Products)')
    
    # Related Product (for sale order)
    product_id = fields.Many2one('product.product', string='المنتج المرتبط (Related Product)',
                                  domain=[('is_engineering_package', '=', True)])

    # Features included in package
    feature_ids = fields.One2many('engineering.package.feature', 'package_id',
                                   string='مميزات الباقة (Package Features)')

    def action_create_product(self):
        """Create a product for this package"""
        self.ensure_one()
        if self.product_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'res_id': self.product_id.id,
                'view_mode': 'form',
            }
        
        # Find or create engineering packages category
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
    
    # Computed fields
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