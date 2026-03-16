# -*- coding: utf-8 -*-
from odoo import models, fields

class EngineeringTaskCommitment(models.Model):
    _name = 'engineering.task.commitment' 
    _description = 'Task Engineering Commitment Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade', required=True)
    
    sign_template_id = fields.Many2one(
        'sign.template', 
        string='Commitment Document (التعهد)', 
        required=True, 
        domain=[('is_commitment', '=', True)]
    )
    
    is_required = fields.Boolean(string='Required (مطلوب)', default=False)
    
    # Stores the final, filled-out PDF document
    sign_request_id = fields.Many2one(
        'sign.request', 
        string='Generated Document (المستند المولد)', 
        readonly=True
    )
