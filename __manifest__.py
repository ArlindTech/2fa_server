{
    'name': 'AMO 2FA Server',
    'summary': 'Handle 2FA requests',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/two_fa_request_views.xml',
        'data/cron.xml',
    ],
    'application': True,
}
