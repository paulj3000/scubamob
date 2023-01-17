SETTING_DISPLAY_MODE = 0

SETTINGS_KEYS = {
    'dark-mode': SETTING_DISPLAY_MODE,
    'display_mode': SETTING_DISPLAY_MODE,
}

SETTINGS = (
    (SETTING_DISPLAY_MODE, 'Display Mode'),
)

SETTINGS_VALUES = {
    SETTING_DISPLAY_MODE: [
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
