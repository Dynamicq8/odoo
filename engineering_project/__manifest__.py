# -*- coding: utf-8 -*-
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
        'sign',
    ],
    'data': [
        'reports/initial_design_report.xml',
        'views/project_project_views.xml',
        'data/project_task_type_data.xml',
        'data/cron.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'engineering_project/static/src/css/task_state.css',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
