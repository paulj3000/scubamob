SYSTEM_APIS = (
    ('ALERTING_SERVER', 'Alerting Server'),
    ('SETTINGS_SERVER', 'Settings Server'),
    ('AWS_SERVER', 'AWS Server'),
    ('BILLING_SERVER', 'Billing Server'),
    ('CHAT_SERVER', 'Chat Server'),
    ('LOGBOOK_SERVER', 'Logbook Server'),
    ('SETTINGS_SERVER', 'Settings Server'),
    ('API_SERVER', 'API Server'),
    ('AWS_S3_BUCKET', 'AWS S3 Bucket'),
    ('AWS_S3_FILE_DELETE', 'AWS S3 File Delete'),
    ('AWS_S3_FILE_HEADERS', 'AWS S3 File Headers'),
    ('AWS_S3_FILE_RENAME', 'AWS S3 File Rename'),
    ('AWS_S3_FILE_UPLOAD', 'AWS S3 File Upload'),
    ('AWS_S3_GEN_POST_URL', 'AWS S3 Generate Post Url'),
    ('AWS_SQS_QUEUE', 'AWS SQS Queue'),
    ('AWS_CLOUDFRONT_URL', 'AWS Cloudfront Url'),
)


ALERTING_APIS = (
    ('ALERTS', 'Alerting Alerts'),
    ('BUDDY_REQUEST', 'Alerting Buddy Request'),
    ('ALERTING_NOTIFY_STAFF', 'Alerting Notify Staff'),
)


AWS_APIS = (
    ('S3_DELETE', 'S3 Delete'),
    ('S3_HEADERS', 'S3 Headers'),
    ('S3_FILE_UPLOAD', 'S3 File Upload'),
    ('S3_FILE_RENAME', 'S3 File Rename'),
    ('S3_GEN_POST_URL', 'S3 Generate Post Url'),
)


BILLING_APIS = (
    ('PROCESSORS', 'Billing Processors'),
    ('AUTHORIZE_CC','Billing Authorize CC'),
)


CHAT_APIS = (
    ('GET_ALL_USER_CHATS', 'Get All User Chats'),
)


LOGBOOK_APIS = (
    ('GET_LOGBOOKS', 'Get All Logbooks'),
    ('GET_LOG', 'Get Log'),
    ('ADD_LOG', 'Add Logbook'),
)


SETTINGS_APIS = (
    ('ADD_USER_SETTING', 'Add User Setting'),
    ('GET_USER_SETTING_LIST', 'Get User Setting List'),
    ('GET_USER_SETTINGS_WITH_OPTIONS', 'Get User Settings with Options'),
    ('POST_USER_SETTINGS', 'Post User Settings'),
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
    ('DEFAULT_PROFILE_IMAGE', 'Default Profile Image'),
]

SOCKET_SERVER_SETTINGS = [
    'SOCKET_SERVER_ACTIVE',
    'SOCKET_SERVER_URL',
    'CHAT_SERVER',
]
