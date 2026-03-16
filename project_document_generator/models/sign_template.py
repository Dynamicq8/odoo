# -*- coding: utf-8 -*-
from odoo import models, fields

class SignTemplate(models.Model):
    _inherit = 'sign.template'

    building_type = fields.Selection([
        ('residential', 'Residential'), 
        ('investment', 'Investment'), 
        ('commercial', 'Commercial'), 
        ('industrial', 'Industrial'), 
        ('cooperative', 'Cooperative'), 
        ('mosque', 'Mosque'), 
        ('hangar', 'Hangar'), 
        ('farm', 'Farm'), 
        ('all', 'All Types')
    ], string="Document Building Type", default='all', help="Type of building this document template is relevant for.")
    
    is_project_document = fields.Boolean(string="Is Project Document?", default=False, 
                                          help="Mark this template if it's used for project document generation.")
