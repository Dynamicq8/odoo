# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
class EngineeringContract(models.Model):
_name = 'engineering.contract'
_description = 'Engineering Contract'
_inherit = ['mail.thread', 'mail.activity.mixin']
_order = 'create_date desc'
code
Code
name = fields.Char(string='رقم العقد (Contract Number)', required=True, copy=False, 
                   readonly=True, default=lambda self: _('New'))

# Related Records
project_id = fields.Many2one('project.project', string='المشروع (Project)', 
                              ondelete='cascade', tracking=True)
sale_order_id = fields.Many2one('sale.order', string='عرض السعر (Quotation)',
                                 related='project_id.sale_order_id', store=True)
partner_id = fields.Many2one('res.partner', string='العميل (Customer)', 
                              required=True, tracking=True)

# Contract Classification
building_type = fields.Selection([
    ('residential', 'سكن خاص (Private Housing)'),
    ('investment', 'استثماري (Investment Building)'),
    ('commercial', 'تجاري (Commercial Building)'),
    ('industrial', 'صناعي (Industrial Building)'),
    ('cooperative', 'جمعيات وتعاونيات (Cooperative)'),
    ('mosque', 'مساجد (Mosques)'),
    ('hangar', 'مخازن / شبرات (Hangar)'),
    ('farm', 'مزارع (Farms)'),
    ('garden', 'حدائق (Garden)'),
    ('shades', 'مظلات (Shades)'),
], string="نوع المبنى (Building Type)", required=True, tracking=True)

service_type = fields.Selection([
    ('new_construction', 'بناء جديد (New Construction)'),
    ('demolition', 'هدم (Demolition)'),
    ('modification', 'تعديل (Modification)'),
    ('extension', 'توسعة (Extension)'),
    ('extension_modification', 'تعديل وتوسعة (Extension & Modification)'),
    ('supervision_only', 'إشراف هندسي فقط (Supervision Only)'),
    ('renovation', 'ترميم (Renovation)'),
    ('internal_partitions', 'قواطع داخلية (Internal Partitions)'),
    ('shades_garden', 'مظلات / حدائق (Shades / Garden)')
], string="نوع الخدمة (Service Type)", required=True, tracking=True)

package_type = fields.Selection([
    ('basic', 'الباقة الأساسية (Basic Package)'),
    ('premium', 'الباقة المميزة (Premium Package)'),
    ('gold', 'الباقة الذهبية (Gold Package)'),
    ('supervision', 'باقة الإشراف (Supervision Package)'),
], string="نوع الباقة (Package Type)", tracking=True)

# Property Details
plot_no = fields.Char(string="رقم القسيمة (Plot)")
block_no = fields.Char(string="القطعة (Block)")
street_no = fields.Char(string="الشارع (Street)")
area = fields.Char(string="المنطقة (Area)")
civil_number = fields.Char(string="الرقم المدني (Civil ID)")

# Contract Content
template_id = fields.Many2one('engineering.contract.template', string='قالب العقد (Contract Template)')
contract_body = fields.Html(string='محتوى العقد (Contract Body)', sanitize=False)
terms_conditions = fields.Html(string='الشروط والأحكام (Terms & Conditions)')

# Financial
contract_amount = fields.Monetary(string='قيمة العقد (Contract Amount)', currency_field='currency_id')
currency_id = fields.Many2one('res.currency', string='Currency', 
                               default=lambda self: self.env.company.currency_id)

# Dates
contract_date = fields.Date(string='تاريخ العقد (Contract Date)', default=fields.Date.today)
start_date = fields.Date(string='تاريخ البدء (Start Date)')
end_date = fields.Date(string='تاريخ الانتهاء (End Date)')

# Status
state = fields.Selection([
    ('draft', 'مسودة (Draft)'),
    ('sent', 'مرسل للتوقيع (Sent for Signature)'),
    ('signed', 'موقع (Signed)'),
    ('active', 'نشط (Active)'),
    ('completed', 'مكتمل (Completed)'),
    ('cancelled', 'ملغي (Cancelled)'),
], string='الحالة (Status)', default='draft', tracking=True)

# Signed Document
signed_document = fields.Binary(string='العقد الموقع (Signed Contract)', attachment=True)
signed_document_name = fields.Char(string='اسم الملف (Filename)')
signature_date = fields.Datetime(string='تاريخ التوقيع (Signature Date)')

@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('engineering.contract') or _('New')
    return super().create(vals_list)

@api.onchange('building_type', 'service_type', 'package_type')
def _onchange_contract_type(self):
    """Auto-select template and fill content based on building/service/package type"""
    if self.building_type and self.service_type:
        template = self.env['engineering.contract.template'].get_template_for_contract(
            self.building_type, self.service_type, self.package_type
        )
        if template:
            self.template_id = template
            self.contract_body = template.contract_body
            self.terms_conditions = template.terms_conditions

@api.onchange('project_id')
def _onchange_project_id(self):
    """Fill contract details from project"""
    for rec in self:
        if rec.project_id:
            # 1. Fill Customer
            rec.partner_id = rec.project_id.partner_id
            
            # 2. Check if the project has a Quotation linked to it
            if rec.project_id.sale_order_id:
                order = rec.project_id.sale_order_id
                rec.building_type = order.building_type
                rec.service_type = order.service_type
                rec.plot_no = order.plot_no
                rec.block_no = order.block_no
                rec.street_no = order.street_no    # <-- Added
                rec.area = order.area
                rec.contract_amount = order.amount_total
                
                if order.partner_id:
                    rec.civil_number = order.partner_id.civil_number  # <-- Added

def action_send_for_signature(self):
    """Send contract for electronic signature via WhatsApp"""
    self.ensure_one()
    if not self.partner_id.phone and not self.partner_id.mobile:
        raise UserError(_("Customer phone number is missing."))
    
    self.state = 'sent'
    
    # Generate WhatsApp link with contract signing message
    phone = self.partner_id.mobile or self.partner_id.phone
    cleaned_phone = ''.join(filter(str.isdigit, phone))
    
    message = _(
        "السلام عليكم %s،\n"
        "نرفق لكم عقد %s رقم %s للمراجعة والتوقيع.\n"
        "يرجى مراجعة العقد والتوقيع عليه."
    ) % (self.partner_id.name, self._get_service_type_name(), self.name)
    
    encoded_message = message.replace('\n', '%0A').replace(' ', '%20')
    whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"
    
    return {
        'type': 'ir.actions.act_url',
        'url': whatsapp_url,
        'target': 'new',
    }

def _get_service_type_name(self):
    """Get Arabic name for service type"""
    service_names = {
        'new_construction': 'بناء جديد',
        'demolition': 'هدم',
        'modification': 'تعديل',
        'extension': 'توسعة',
        'extension_modification': 'تعديل وتوسعة',
        'supervision_only': 'إشراف هندسي',
        'renovation': 'ترميم',
        'internal_partitions': 'قواطع داخلية',
        'shades_garden': 'مظلات / حدائق',
    }
    return service_names.get(self.service_type, '')

def action_mark_signed(self):
    """Mark contract as signed"""
    self.ensure_one()
    self.write({
        'state': 'signed',
        'signature_date': fields.Datetime.now(),
    })
    return True

def action_activate(self):
    """Activate the contract"""
    self.ensure_one()
    if self.state != 'signed':
        raise UserError(_("Contract must be signed before activation."))
    self.state = 'active'
    return True

def action_complete(self):
    """Mark contract as completed"""
    self.ensure_one()
    self.state = 'completed'
    return True

def action_cancel(self):
    """Cancel the contract"""
    self.ensure_one()
    self.state = 'cancelled'
    return True

def action_reset_to_draft(self):
    """Reset to draft"""
    self.ensure_one()
    self.state = 'draft'
    return True

def action_print_contract(self):
    """Print contract PDF"""
    return self.env.ref('engineering_contracts.action_report_engineering_contract').report_action(self)

def action_send_whatsapp(self):
    """Send contract link via WhatsApp"""
    self.ensure_one()
    if not self.partner_id.phone and not self.partner_id.mobile:
        raise UserError(_("Customer phone number is missing."))
    
    phone = self.partner_id.mobile or self.partner_id.phone
    cleaned_phone = ''.join(filter(str.isdigit, phone))
    
    # Get base URL
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    contract_url = f"{base_url}/web#id={self.id}&model=engineering.contract&view_type=form"
    
    message = _(
        "السلام عليكم،\n"
        "يمكنكم مراجعة العقد رقم %s من خلال الرابط التالي:\n%s"
    ) % (self.name, contract_url)
    
    encoded_message = message.replace('\n', '%0A').replace(' ', '%20')
    whatsapp_url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_message}"
    
    return {
        'type': 'ir.actions.act_url',
        'url': whatsapp_url,
        'target': 'new',
    }
