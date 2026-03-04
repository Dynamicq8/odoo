{
    'name': "Engineering Project Enhancements",
    'summary': "Links projects to sales orders and manages engineering project workflows.",
    'author': "Engineering Office",
    'category': 'Services/Engineering',
    'version': '17.0.1.0.0',
    'depends': [
        'project',
        'sale_management',
        'engineering_core',
    ],
    'data': [
        'reports/initial_design_report.xml', # <--- ADD THIS
        'views/project_project_views.xml',
        'data/project_task_type_data.xml',

    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
