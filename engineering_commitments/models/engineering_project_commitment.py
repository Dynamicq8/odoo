# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

# =========================================================
# NEW 🚀: COMMITMENT MODEL FOR PROJECTS
# This is a new model specifically for project-level commitments.
# =========================================================
class EngineeringProjectCommitment(models.Model):
    _name = 'engineering.project.commitment'
    _description = 'Project Commitment'

    project_id = fields.Many2one('project.project', ondelete='cascade')
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
