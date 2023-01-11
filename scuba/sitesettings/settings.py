SYSTEM_APIS = (
    ('ALERTING_ALERTS',         'Alerting Alerts'),
    ('ALERTING_BUDDY_REQUEST',  'Alerting Buddy Request'),
    ('ALERTING_NOTIFY_STAFF',   'Alerting Notify Staff'),

    ('ALERTING_SERVER',     'Alerting Server'),
    ('SETTINGS_SERVER',     'Settings Server'),
    ('CHAT_SERVER',         'Chat Server'),
    ('DIVE_SERVER',         'Dive Server'),
    ('SETTINGS_SERVER',     'Settings Server'),
    ('API_SERVER',          'API Server'),
    ('AWS_S3_BUCKET',       'AWS S3 Bucket'),
    ('AWS_S3_FILE_DELETE',  'AWS S3 File Delete'),
    ('AWS_S3_FILE_HEADERS', 'AWS S3 File Headers'),
    ('AWS_S3_FILE_RENAME',  'AWS S3 File Rename'),
    ('AWS_S3_FILE_UPLOAD',  'AWS S3 File Upload'),
    ('AWS_S3_GEN_POST_URL', 'AWS S3 Generate Post Url'),
    ('AWS_SQS_QUEUE',       'AWS SQS Queue'),
    ('AWS_CLOUDFRONT_URL',  'AWS Cloudfront Url'),

    ('BILLING_PROCESSORS',  'Billing Processors'),
    ('BILLING_AUTHORIZE_CC', 'Billing Authorize CC'),
)

DIVELOG_APIS = (
    ('GET_DIVELOGS', 'Get Dive Logs'),
    ('ADD_DIVELOG', 'Add Dive Logs'),
)

SETTINGS_APIS = (
    ('ADD_USER_SETTING', 'Add User Setting'),
    ('GET_USER_SETTING_LIST', 'Get User Setting List'),
    ('GET_USER_SETTINGS_WITH_OPTIONS', 'Get User Settings with Options'),
    ('POST_USER_SETTINGS', 'Post User Settings'),
)

SYSTEM_SETTINGS = [
    ('CHAT_SERVER_ACTIVE', 'Chat Server Active'),
]

SOCKET_SERVER_SETTINGS = [
    'SOCKET_SERVER_ACTIVE',
    'SOCKET_SERVER_URL',
    'CHAT_SERVER',
]
