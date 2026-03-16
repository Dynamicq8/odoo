# models/sign_template_extension.py
from odoo import models, fields

class SignTemplate(models.Model):
    _inherit = 'sign.template'

    is_commitment = fields.Boolean(
        string='Is Commitment',
        help='If checked, this template can be used as an engineering commitment for tasks.'
    )

    building_type = fields.Selection([
        ('residential', 'Residential (سكني)'),
        ('commercial', 'Commercial (تجاري)'),
        ('industrial', 'Industrial (صناعي)'),
        ('all', 'All Types (جميع الأنواع)'),
    ], string='Building Type', default='all',
       help="Filter templates based on the building type of the project.")
