{
    'name': "Engineering Quotation Pipeline",
    'summary': "Manages custom stages, pipeline, and workflows for engineering quotations.",
    'author': "Engineering Office",
    'website': "https://www.yourcompany.com",
    'category': 'Services/Engineering',
    'version': '17.0.1.0.0',
    'depends': [
        'engineering_core',
        'sale_management',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/engineering_quotation_stage_data.xml',
        'views/engineering_quotation_stage_views.xml',
        'views/sale_order_views.xml',
        'report/quotation_report.xml',
        'report/quotation_templates.xml',
        'views/sale_portal_templates.xml',  # <--- ADD THIS LINE

    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
