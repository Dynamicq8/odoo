{
    'name': "Sign Template Renamer",
    'version': '1.0',
    'category': 'Sign',
    'summary': 'Helper to rename sign template fields when UI is buggy.',
    'depends': ['sign'], # Depends on the sign module
    'data': [
        'views/sign_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
