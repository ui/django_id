import settings, os

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])
MEDIA_ROOT = os.path.join(os.path.dirname(PROJECT_PATH.rstrip('/')), 'media')

#DEBUG = False
#TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'db_name',
        'USER': 'root',
        'PASSWORD': 'PASSWORD',
        'HOST': '',
        'PORT': '',
    }
}


#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.example.com'
#EMAIL_HOST_USER = 'user@example.com'
#EMAIL_HOST_PASSWORD = 'password'
#EMAIL_PORT = 587
#DEFAULT_FROM_EMAIL = 'from@example.com'
