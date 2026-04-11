# models/company_seal.py
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    company_seal_image = fields.Binary(
        string="Company Seal Image",
        help="Upload the image for the company seal. This will be automatically filled into 'Seal' fields."
    )
    company_seal_filename = fields.Char(
        string="Company Seal Filename"
    )