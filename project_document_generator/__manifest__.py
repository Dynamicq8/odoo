{
    'name': "Project Document Generator",
    'summary': "Generate and autofill project-related documents using Sign templates.",
    'version': '1.0',
    'category': 'Project',
    'depends': [
        'base',
        'web',
        'sign',
        'project',
        # Assuming 'engineering_project' contains project_id.building_type, governorate_id, etc.
        'engineering_project', 
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sign_template_views.xml', # For extending sign.template
        'views/project_document_pledge_views.xml',
        'views/project_task_views.xml', # For adding pledge_ids to project.task form
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3', # Don't forget the license!
}
