# -*- coding: utf-8 -*-
{
    'name': "Engineering Commitments",
    'summary': "Manage Municipality Commitments & Autofill PDFs via Sign App",
    'version': '1.0',
    'category': 'Services/Project',
    'depends': [
        'base',
        'sign',
        'project',
        'engineering_project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sign_template_views.xml',
        'reports/project_commitment_report.xml', # <-- Make sure this line is exactly here
        'views/report_project_commitment_document.xml', # <-- Make sure this line is exactly here
        'views/project_task_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'engineering_commitments/static/src/views/sign_template_form_view.js',
            'engineering_commitments/static/src/xml/sign_template_form_fields.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
