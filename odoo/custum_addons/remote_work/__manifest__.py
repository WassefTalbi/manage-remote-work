

{
    'name': 'work distance',
    'version': '17.0.0.1.0',
    'category': 'Human Resources',
     'author':'Wassef Talbi',
    'summary': 'manage the remote work ',


    'depends': ['base','hr_attendance','web','calendar'],
    'data': [
         'security/ir.model.access.csv',
         'security/remote_work_rules.xml',
         'views/checkin_checkout_wizard_views.xml',
         'views/pause_reprise_wizard_views.xml',
         'views/hr_break_wizard_views.xml',
         'views/remote_work_request_views.xml',
         'views/hr_attendance_menus.xml',




    ],
       'assets': {
        'web.assets_backend': [
            'remote_work/static/src/js/remote_work_calendar.js',
            'remote_work/static/src/css/remote_work_calendar.css',
            'remote_work/static/src/css/remote_work_kanban.css',
        ],
    },
    'application': True,



}
