# Django settings for webui project.
import os

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# This is shown when an error 500 occurs.
EMAIL_SUPPORT = 'support@example.com'

# People who get error notifications.
ADMINS = (
	# ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'livemgr',
		'USER': 'livemgr',
		'PASSWORD': 'livemgr',
		'HOST': '',
		'PORT': '',
	}
}

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/SaoPaulo'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
	('en', gettext_noop('English')),
	('pt-BR', gettext_noop('Brazilian Portuguese')),
)
USE_I18N = True
USE_L10N = True

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, os.pardir, 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&7*k_v2egx#qhzjt6g0j+-+dr5cc50f+f7p5eafp&2e)uz(xxr'

# Applied in reverse order.
MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'webui.urls'

# Search order.
TEMPLATE_DIRS = ()

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.admin',
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

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# General stuff
INTERNAL_IPS = ('127.0.0.1',)
CSRF_FAILURE_VIEW = 'webui.livemgr.controllers.profiles.no_cookie'

# Authentication
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/dashboard'
AUTH_PROFILE_MODULE = 'livemgr.Profile'

# Keyserver
LICENSE_FILE = ''
KEYSERVER_HOST = ''
KEYSERVER_PORT = 443
KEYSERVER_USE_SSL = True
KEYSERVER_TIMEOUT = 5 # Seconds
