# -*- coding: utf-8 -*-
from odoo import models, fields, api

# ==============================================================================
#  RES PARTNER - This part is fine, no changes needed
# ==============================================================================
class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار", tracking=True)
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('extension', 'توسعة'), ('extension_modification', 'تعديل وتوسعة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة", tracking=True)
    civil_number = fields.Char(string="الرقم المدني (Civil ID)")
    plot_no = fields.Char(string="رقم القسيمة (Plot)")
    block_no = fields.Char(string="القطعة (Block)")
    street_no = fields.Char(string="الشارع (Street)")
    area = fields.Char(string="المساحة (Area)")


# ==============================================================================
#  CRM LEAD - Added a function to copy data to new quotations
# ==============================================================================
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار")
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('extension', 'توسعة'), ('extension_modification', 'تعديل وتوسعة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة")
    plot_no = fields.Char(string="رقم القسيمة (Plot)")
    block_no = fields.Char(string="القطعة (Block)")
    street_no = fields.Char(string="الشارع (Street)")
    area = fields.Char(string="المساحة (Area)")
    
    # --- NEW FUNCTION ---
    # This runs when you click 'New Quotation' from a CRM Lead
    def _prepare_sale_order_values(self, partner, company, access_token):
        # First, get all the standard values Odoo prepares
        values = super()._prepare_sale_order_values(partner, company, access_token)
        
        # Now, add our custom engineering fields to the list of values to be copied
        if self.building_type:
            values['building_type'] = self.building_type
        if self.service_type:
            values['service_type'] = self.service_type
        if self.plot_no:
            values['plot_no'] = self.plot_no
        if self.block_no:
            values['block_no'] = self.block_no
        if self.street_no:
            values['street_no'] = self.street_no
        if self.area:
            values['area'] = self.area
            
        return values


# ==============================================================================
#  SALE ORDER - This is where the main fix is. Fields are no longer 'related'.
# ==============================================================================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # --- THE FIX ---
    # Removed 'related=...' from all fields. They are now independent and fully editable.
    # The function above in CrmLead handles copying the data initially.
    
    building_type = fields.Selection([('residential', 'سكن خاص'), ('investment', 'استثماري'), ('commercial', 'تجاري'), ('industrial', 'صناعي'), ('cooperative', 'جمعيات وتعاونيات'), ('mosque', 'مساجد'), ('hangar', 'مخازن / شبرات'), ('farm', 'مزارع')], string="نوع العقار", store=True)
    service_type = fields.Selection([('new_construction', 'بناء جديد'), ('demolition', 'هدم'), ('modification', 'تعديل'), ('extension', 'توسعة'), ('extension_modification', 'تعديل وتوسعة'), ('supervision_only', 'إشراف هندسي فقط'), ('renovation', 'ترميم'), ('internal_partitions', 'قواطع داخلية'), ('shades_garden', 'مظلات / حدائق')], string="نوع الخدمة", store=True)

    plot_no = fields.Char(string="رقم القسيمة", store=True)
    block_no = fields.Char(string="القطعة", store=True)
    street_no = fields.Char(string="الشارع", store=True)
    area = fields.Char(string="المساحة", store=True)
