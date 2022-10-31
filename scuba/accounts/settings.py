SETTING_DARK_MODE = 0

SETTINGS_KEYS = {
    'dark-mode': SETTING_DARK_MODE,
}

SETTINGS = (
    (SETTING_DARK_MODE, 'Dark Mode'),
)

SETTINGS_VALUES = {
    SETTING_DARK_MODE: [
        {
            'title': 'Device Settings',
            'default': True
        },
        {
            'title': 'Dark Mode',
        },
        {
            'title': 'Light Mode',
        }
    ]
}
