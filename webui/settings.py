# -*- coding: utf-8 -*-

# Django settings for webui project.

import os.path
ROOT = os.path.dirname(os.path.abspath(__file__))

_ = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test',
        'USER': 'jane',
        'PASSWORD': 'doe',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = None

# Language section
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', _('English')),
    ('pt-br', _('Brazilian Portuguese')),
)
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(ROOT, '..', 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

# FIXME: ???
SECRET_KEY = '2m74tbo+#7iin(h(nn2d!#=bryc8w*3e9+&7(%g7o5yd*hy-en'

# code config

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'webui.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.webdesign',
    'django_tables',
    'webui.common',
    'webui.livemgr',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.csrf',
)

# Authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/dashboard'
AUTH_PROFILE_MODULE = 'livemgr.Profile'

# General stuff
INTERNAL_IPS = ('127.0.0.1', )
CSRF_FAILURE_VIEW = 'webui.livemgr.controllers.profiles.no_cookie'

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# This is shown when an error 500 occurs.
EMAIL_SUPPORT = 'support@example.com'

# Keyserver
LICENSE_FILE = ''
KEYSERVER_HOST = ''
KEYSERVER_PORT = 443
KEYSERVER_USE_SSL = True
KEYSERVER_TIMEOUT = 5 # seconds
