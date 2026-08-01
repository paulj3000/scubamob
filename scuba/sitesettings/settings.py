SYSTEM_APIS = (
    ('SETTINGS_SERVER', 'Settings Server'),
    ('CHAT_SERVER', 'Chat Server'),
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
    ('AUTHORIZE_CC', 'Billing Authorize CC')
)


CHAT_APIS = (
    ('CHAT_LOOKUP', 'Chat Lookup'),
    ('CREATE_CHAT', 'Create Chat'),
    ('GET_ALL_USER_CHATS', 'Get All User Chats'),
    ('GET_ALL_CHAT_MESSAGES', 'Get All Chat Messages'),
    ('ADMIN_GET_ALL_CHATS', 'Admin Get All Chats'),
)


LOGBOOK_APIS = (
    ('GET_LOGBOOKS', 'Get All Logbooks'),
    ('GET_LOG', 'Get Log'),
    ('ADD_LOG', 'Add Logbook'),
    ('GET_TAGS', 'Get All TAGS'),
    ('GET_ALL_TEMPLATES', 'Get All Templates'),
    ('GET_TEMPLATE', 'Get Template'),
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
    ('ALERT_SERVER_ACTIVE', 'Alert Server Active'),
    ('DEFAULT_PROFILE_IMAGE', 'Default Profile Image'),
    ('DEFAULT_BANNER_IMAGE', 'Default Banner Image'),
]

SOCKET_SERVER_SETTINGS = [
    'SOCKET_SERVER_ACTIVE',
    'SOCKET_SERVER_URL',
    'CHAT_SERVER',
]

APPS = [
    ('DIVESITE', 'Dive Site'),
    ('HOME', 'Home'),
    ('LOGBOOK', 'Logbook'),
    ('USER', 'User'),
]
