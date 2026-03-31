# -*- coding: utf-8 -*-
from odoo import models, fields

class SignTemplate(models.Model):
    _inherit = 'sign.template'

    building_type = fields.Selection([
        ('residential', 'سكن خاص'), ('investment', 'استثماري'), 
        ('commercial', 'تجاري'), ('industrial', 'صناعي'), 
        ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), 
        ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع'), ('all', 'جميع الأنواع')
    ], string="Building Type (نوع العقار)", default='all')
    
    # ADDED SERVICE TYPE FIELD
    service_type = fields.Selection([
        ('new_construction', 'بناء جديد'), 
        ('demolition', 'هدم'), 
        ('modification', 'تعديل'), 
        ('addition', 'اضافة'), 
        ('addition_modification', 'تعديل واضافة'), 
        ('supervision_only', 'إشراف هندسي فقط'), 
        ('renovation', 'ترميم'), 
        ('internal_partitions', 'قواطع داخلية'), 
        ('shades_garden', 'مظلات / حدائق'),
        ('all', 'جميع الأنواع') # Added 'all' for service type as well
    ], string="Service Type (نوع الخدمة)", default='all')
    
    is_commitment = fields.Boolean(string="Is Engineering Commitment? (تعهد هندسي؟)", default=True)