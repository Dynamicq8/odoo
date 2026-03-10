{
    'name': "Engineering Pledges",
    'summary': "Manage Municipality Pledges (تعهدات البلدية)",
    'version': '1.0',
    'category': 'Services/Project',
'depends': ['base', 'project', 'engineering_project'], # Added engineering_project
    'data': [
        'security/ir.model.access.csv',
        'views/pledge_template_views.xml',
                'views/project_views.xml', # We will create this file in Step 4

    ],
    'installable': True,
    'application': False,
}
