import os


# Invite
SMTP_PORT = 465
SENDER_EMAIL = 'fikfok' + '@' + 'mail.ru'
SENDER_PASSWORD = os.environ.get('SMTP_EMAIL_PASSOWRD')
SMTP_SERVER = 'smtp.mail.ru'

# Yandex maps
YANDEX_GEOCODE_MAP_URL = 'https://geocode-maps.yandex.ru/1.x'
YANDEX_API_KEY = '125708d6-baa6-407e-b906-d8be0fca76b2'
MAP_WIDTH_PX = 350
MAP_HEIGHT_PX = 350

# Dadata
DADATA_TOKEN = os.environ.get('DADATA_TOKEN')
