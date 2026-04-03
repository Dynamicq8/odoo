# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EngineeringTaskCommitment(models.Model):
    _name = 'engineering.task.commitment'
    _description = 'Task Commitment'

    task_id = fields.Many2one('project.task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', required=True)
    sign_request_id = fields.Many2one('sign.request')
    is_required = fields.Boolean("Required")

    def action_sign_now(self):
        self.ensure_one()
        if not self.sign_request_id:
            raise UserError(_("No generated document yet."))
            
        request = self.sign_request_id
        user = self.env.user
        
        # Check permissions
        is_admin = user.has_group('base.group_system')
        # Check if user has a secretary_id (using getattr to avoid errors if field doesn't exist)
        is_secretary = bool(getattr(user, 'secretary_id', False))
        
        if is_admin or is_secretary:
            request_item = request.request_item_ids[:1]
        else:
            request_item = request.request_item_ids.filtered(
                lambda r: r.partner_id.id == user.partner_id.id
            )
            
        if not request_item:
            raise UserError(_("You are not assigned to sign this document."))
            
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request_item[0].access_token}',
            'target': 'new',
        }

class EngineeringTaskCompanyContract(models.Model):
    _name = 'engineering.task.contract'   # CHANGED FROM 'engineering.task.company.contract'
    _description = 'Engineering Task Company Contract Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if not self.sign_request_id:
            raise UserError(_("No generated document yet."))
            
        request = self.sign_request_id
        user = self.env.user
        
        is_admin = user.has_group('base.group_system')
        is_secretary = bool(getattr(user, 'secretary_id', False))
        
        if is_admin or is_secretary:
            request_item = request.request_item_ids[:1]
        else:
            request_item = request.request_item_ids.filtered(
                lambda r: r.partner_id.id == user.partner_id.id
            )
            
        if not request_item:
            raise UserError(_("You are not assigned to sign this document."))
            
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request_item[0].access_token}',
            'target': 'new',
        }

# =========================================================
# NEW: PHASES APPROVAL MODEL FOR TASKS
# =========================================================
class EngineeringTaskPhaseApproval(models.Model):
    _name = 'engineering.task.phase.approval'
    _description = 'Engineering Task Phase Approval Line'

    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    sign_template_id = fields.Many2one('sign.template', string='Template', required=True)
    is_required = fields.Boolean(string='Required', default=False)
    sign_request_id = fields.Many2one('sign.request', string='Sign Request')

    def action_sign_now(self):
        self.ensure_one()
        if not self.sign_request_id:
            raise UserError(_("No generated document yet."))
            
        request = self.sign_request_id
        user = self.env.user
        
        is_admin = user.has_group('base.group_system')
        is_secretary = bool(getattr(user, 'secretary_id', False))
        
        if is_admin or is_secretary:
            request_item = request.request_item_ids[:1]
        else:
            request_item = request.request_item_ids.filtered(
                lambda r: r.partner_id.id == user.partner_id.id
            )
            
        if not request_item:
            raise UserError(_("You are not assigned to sign this document."))
            
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sign/document/{request.id}/{request_item[0].access_token}',
            'target': 'new',
        }