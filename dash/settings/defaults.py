import os
here = lambda * x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

PROJECT_ROOT = here('..')

root = lambda * x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)

PROJECT_MODULE = '.'.join(__name__.split('.')[:-2])  # cut .settings.base


DEBUG = True

TEMPLATE_DEBUG = DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': root('etc', 'development.db'),
    }
}

MEDIA_ROOT = root('static', 'uploads')
MEDIA_URL = '/static/uploads/'

STATIC_ROOT = root('static', 'assets')
STATIC_URL = '/static/assets/'

ADMIN_MEDIA_PREFIX = '/static/assets/admin/'

STATICFILES_DIRS = (
    root('staticfiles'),
)

ROOT_URLCONF = '%s.settings.urls' % PROJECT_MODULE

TEMPLATE_DIRS = (
    root('templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # external
    'south',

    # internal
    # 'app1',
)

SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s |'
                       ' %(pathname)s:%(lineno)d (in %(funcName)s) |'
                       ' %(message)s ')
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': root('%s.log' % PROJECT_MODULE),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        PROJECT_MODULE: {
            'handlers': ['logfile'],
            'level': 'DEBUG'
        }
    }
}

TEST_EXCLUDE = ('django',)
TEST_RUNNER = '%s.settings.test_suite.AdvancedTestSuiteRunner' % PROJECT_MODULE


