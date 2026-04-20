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
            'engineering_quotation',   # ← ADD THIS

    ],
    'data': [
        'reports/initial_design_report.xml',
        'views/project_project_views.xml',
        'data/project_task_type_data.xml',
        'data/cron.xml',
        'reports/report_project_description.xml',
        'security/ir.model.access.csv',

    ],
    'assets': {
        'web.assets_backend': [
            'engineering_project/static/src/css/task_state.css',
            'engineering_project/static/lib/fabric/fabric.min.js',
            # 2. Load our custom JS widget
            'engineering_project/static/src/js/sketch_pad_widget.js',
            # 3. Load our custom OWL template
            'engineering_project/static/src/xml/sketch_pad_widget.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
