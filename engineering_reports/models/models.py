# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import urllib.parse


# ================================
# Site Visit Report Model
# ================================
class EngineeringSiteVisit(models.Model):
    _name = 'engineering.site.visit'
    _description = 'Site Visit Report'
    _order = 'visit_date desc'

    name = fields.Char(
        string='Report Title',
        required=True,
        default=lambda self: _('Site Visit Report - %s' % fields.Date.today())
    )
    
    # الروابط الرئيسية
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    task_id = fields.Many2one('project.task', string='Related Task', ondelete='set null')
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='project_id.partner_id',
        readonly=True,
        store=True
    )

    # بيانات التقرير
    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now, required=True)
    visitor_id = fields.Many2one(
        'res.users',
        string='Engineer/User',
        default=lambda self: self.env.user,
        required=True
    )
    
    # ملف التقرير
    pdf_report = fields.Binary(string="ملف التقرير (صورة أو PDF) - Report File", attachment=True)
    pdf_filename = fields.Char(string="اسم الملف (Filename)")

    # حالة الإرسال
    sent_to_customer = fields.Boolean(string='Sent to Customer', readonly=True)
    sent_date = fields.Datetime(string='Sent Date', readonly=True)

    # إرسال واتساب
    def action_generate_whatsapp_redirect_report(self):
        self.ensure_one()

        customer_phone = self.customer_id.mobile or self.customer_id.phone
        if not customer_phone:
            raise UserError(_("رقم الهاتف مفقود (Customer phone missing)."))

        if not self.pdf_report:
            raise UserError(_("يرجى رفع ملف التقرير (صورة أو PDF) أولاً قبل الإرسال.\nPlease upload the report file before sending."))

        cleaned_phone = ''.join(filter(str.isdigit, customer_phone))

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        safe_filename = urllib.parse.quote(self.pdf_filename or 'Report_File')
        download_link = f"{base_url}/web/content/engineering.site.visit/{self.id}/pdf_report/{safe_filename}"

        message = _("مرحباً،\nنرفق لكم تقرير الزيارة الميدانية: %s\nيمكنكم عرض أو تحميل المرفق عبر الرابط التالي:\n%s") % (
            self.name, download_link
        )

        encoded_msg = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_msg}"

        self.write({
            'sent_to_customer': True,
            'sent_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }


# ================================
# Extend Project Task
# ================================
class ProjectTask(models.Model):
    _inherit = 'project.task'

    site_visit_report_ids = fields.One2many(
        'engineering.site.visit',
        'task_id',
        string='Site Visit Reports'
    )

    # ✅ NEW: Visibility control (Odoo 17 required)
    show_site_visit_reports = fields.Boolean(
        compute="_compute_show_site_visit_reports",
        store=False
    )

    @api.depends('workflow_step')
    def _compute_show_site_visit_reports(self):
        allowed_steps = {'nra_5_1', 'nrn_5_2', 'rn_5_2'}
        for rec in self:
            rec.show_site_visit_reports = rec.workflow_step in allowed_steps

    # إنشاء تقرير زيارة
    def action_create_site_visit_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'engineering.site.visit',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_task_id': self.id,
                'default_project_id': self.project_id.id,
                'default_name': _('Site Visit Report - %s' % self.project_id.name),
            },
        }