# -*- coding: utf-8 -*-
{
    'name': "Show Payment Balance",

    'summary': """
    """,

    'description': """
      """,

    'author': "Milwell",
    'website': "https://github.com/milwell/show_payment_balance",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}