{
    'name': "Engineering Packages & Bundles",
    'summary': "Product packages and bundles for engineering services.",
    'description': """
        نظام الباقات الهندسية
        =====================
        - إنشاء قسم باقات داخل المنتجات
        - تصنيف الباقات ضمن Product Categories
        - إمكانية تكوين الباقة من عدة منتجات (Bundle)
        - إمكانية إضافة الباقات بسهولة داخل عرض السعر
        - الباقة الأساسية، الباقة المميزة، الباقة الذهبية
    """,
    'author': "Engineering Office",
    'website': "https://www.yourcompany.com",
    'category': 'Services/Engineering',
    'version': '17.0.1.0.0',
    'depends': [
        'engineering_core',
        'sale_management',
        'product',
        'uom',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_category_data.xml',
        'data/engineering_package_data.xml',
        'views/engineering_package_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/sale_portal_templates.xml',     # <-- ADDED THIS
        'views/custom_sale_report.xml', # <-- RENAMED/NEW FILE

    ],
       'assets': {
        'web.report_assets_common': [
            'engineering_packages/static/src/css/report.css',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
