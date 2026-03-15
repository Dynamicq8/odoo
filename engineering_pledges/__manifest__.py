{
    'name': "Engineering Pledges",
    'summary': "Manage Municipality Pledges (تعهدات البلدية)",
    'version': '1.0',
    'category': 'Services/Project',
    'depends': [
        'base',
        'web',
        'sign',
        'project',
        'engineering_project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/pledges_report.xml',
        'views/pledge_template_views.xml',
        'views/project_views.xml',
    ],
    'installable': True,
    'application': False,
}
