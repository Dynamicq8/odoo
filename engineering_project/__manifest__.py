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
        'sign', # <--- ADDED THIS!
                'engineering_commitments', # <--- ADD THIS LINE! This is the fix for the current error.

    ],
    'data': [
        # Ensure views and data that define or use models are loaded first
        'reports/initial_design_report.xml',
        'views/project_project_views.xml', # This file contains the view for your new model
        'data/project_task_type_data.xml',
        'data/cron.xml',
        # Move security file to the very end
        'security/ir.model.access.csv', # <--- MOVED THIS TO THE END
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
