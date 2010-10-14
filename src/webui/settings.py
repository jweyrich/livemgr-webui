# Django settings for webui project.
from socket import gethostname
import os
import stat

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
#print 'PROJECT_PATH=%s' % PROJECT_PATH
#VIRTUALENV = "/Users/jweyrich/Desktop/webui/lib/python2.6/site-packages"

# DONT CHANGE THESE
SITE_ID = 1
ROOT_URLCONF = 'webui.urls'

####################
# CORE             #
####################

DEBUG = True #True
TEMPLATE_DEBUG = True

# Whether the framework should propagate raw exceptions rather than catching
# them. This is useful under some testing situations and should never be used
# on a live site.
DEBUG_PROPAGATE_EXCEPTIONS = False

# People who get code error notifications.
# In the format (('Full Name', 'email@domain.com'), ('Full Name', 'anotheremail@domain.com'))
ADMINS = (
# 	('Jardel Weyrich', 'jweyrich@gmail.com'),
# 	('William Lima', 'wlima@primate.com.br'),
)

EMAIL_SUPPORT = 'support@example.com'

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ('127.0.0.1', '10.1.1.16', '192.168.1.100', '192.168.1.101')

# Local time zone for this installation. All choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities).
TIME_ZONE = 'America/SaoPaulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Languages we provide translations for, out of the box. The language name
# should be the utf-8 encoded local name for the language.
LANGUAGES = (
 	('en', gettext_noop('English')),
 	('pt-br', gettext_noop('Brazilian Portuguese')),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LOCALE_PATHS = ()
LANGUAGE_COOKIE_NAME = 'django_language'

# If you set this to True, Django will format dates, numbers and calendars
# according to user current locale
USE_L10N = True

# E-mail address that error messages come from.
SERVER_EMAIL = 'root@localhost'

# Whether to send broken-link e-mails.
SEND_BROKEN_LINK_EMAILS = False

DATABASE_CONFIG_FILE = PROJECT_PATH+'/conf/mysql-%s.conf' % gethostname().split('.')[0]
if not os.path.isfile(DATABASE_CONFIG_FILE):
	raise Exception("Database configuration file for this host does not exist: %s" % DATABASE_CONFIG_FILE)

# Database connection info.
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'OPTIONS': {
			'read_default_file': DATABASE_CONFIG_FILE
		}
	}
# 	'default': {
# 		'ENGINE': 'django.db.backends.mysql',	# Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# 		'NAME': 'schema',						# Or path to database file if using sqlite3.
# 		'USER': 'user',							# Not used with sqlite3.
# 		'PASSWORD': 'pass',						# Not used with sqlite3.
# 		'HOST': '',								# Set to empty string for localhost. Not used with sqlite3.
# 		'PORT': '',								# Set to empty string for default. Not used with sqlite3.
# 	}
}


# The email backend to use. For possible shortcuts see django.core.mail.
# The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending e-mail.
EMAIL_HOST = 'localhost'

# Port for sending e-mail.
EMAIL_PORT = 25

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# Default e-mail address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'webui@localhost'

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[Django] '

# List of strings representing installed apps.
INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.admin',
	'django.contrib.webdesign',
	'django_tables',
	'debug_toolbar',
	'webui.common',
	'webui.imdata',
)

# List of locations of the template source files, in search order.
TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_PATH, 'templates'),
	os.path.join(PROJECT_PATH, 'imdata/templates'),
)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.request',
	'django.contrib.messages.context_processors.messages',
	'django.core.context_processors.csrf',
)

# Force the URL prefix ('' serves under '/')
#FORCE_SCRIPT_NAME = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Whether to append trailing slashes to URLs.
APPEND_SLASH = True

# A secret key for this particular Django installation. Used in secret-key
# hashing algorithms. Set this in your settings, or Django will complain
# loudly.
# Make this unique, and don't share it with anybody.
SECRET_KEY = '&7*k_v2egx#qhzjt6g0j+-+dr5cc50f+f7p5eafp&2e)uz(xxr'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

##############
# MIDDLEWARE #
##############

# List of middleware classes to use.  Order is important; in the request phase,
# this middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	#'django.middleware.csrf.CsrfResponseMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.locale.LocaleMiddleware',
#     'django.middleware.http.ConditionalGetMiddleware',
#     'django.middleware.gzip.GZipMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

############
# SESSIONS #
############

SESSION_COOKIE_NAME = 'sessionid'                       # Cookie name. This can be whatever you want.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2               # Age of cookie, in seconds (default: 2 weeks).
SESSION_COOKIE_DOMAIN = None                            # A string like ".lawrence.com", or None for standard domain cookie.
SESSION_COOKIE_SECURE = False                           # Whether the session cookie should be secure (https:// only).
SESSION_COOKIE_PATH = '/'                               # The path of the session cookie.
SESSION_SAVE_EVERY_REQUEST = False                      # Whether to save the session data on every request.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False                 # Whether a user's session cookie expires when the Web browser is closed.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # The module to store session data
SESSION_FILE_PATH = None                                # Directory to store session files if using the file session module. If None, the backend will use a sensible default.

#########
# CACHE #
#########

# The cache backend to use.  See the docstring in django.core.cache for the
# possible values.
CACHE_BACKEND = 'locmem://'
CACHE_MIDDLEWARE_KEY_PREFIX = ''
CACHE_MIDDLEWARE_SECONDS = 600

##################
# AUTHENTICATION #
##################

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/dashboard'
AUTH_PROFILE_MODULE = 'imdata.Profile'

# The number of days a password reset link is valid for
PASSWORD_RESET_TIMEOUT_DAYS = 3

########
# CSRF #
########

# Dotted path to callable to be used as view when a request is
# rejected by the CSRF middleware.
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Name and domain for CSRF cookie.
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_DOMAIN = None

############
# MESSAGES #
############

# Class to use as messges backend
#MESSAGE_STORAGE = 'django.contrib.messages.storage.user_messages.LegacyFallbackStorage'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

###############
# FILE UPLOAD #
###############

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 # 1 MB
FILE_UPLOAD_TEMP_DIR = None # None = '/tmp'
FILE_UPLOAD_PERMISSIONS = stat.S_IRUSR | stat.S_IWUSR # u+rw

########################
# DJANGO DEBUG TOOLBAR #
########################

#DEBUG_TOOLBAR_PANELS = (
#    'debug_toolbar.panels.version.VersionDebugPanel',
#    'debug_toolbar.panels.timer.TimerDebugPanel',
#    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
#    'debug_toolbar.panels.headers.HeaderDebugPanel',
#    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
#    'debug_toolbar.panels.template.TemplateDebugPanel',
#    'debug_toolbar.panels.sql.SQLDebugPanel',
#    'debug_toolbar.panels.signals.SignalDebugPanel',
#    'debug_toolbar.panels.logger.LoggingPanel',
#)

def show_toolbar(request):
	user = request.user
	if hasattr(user, 'get_profile'):
		return user.get_profile().debug
	return False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'HIDE_DJANGO_SQL': False,
}
