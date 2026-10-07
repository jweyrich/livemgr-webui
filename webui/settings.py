# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Jardel Weyrich
#
# This file is part of livemgr-webui.
#
# livemgr-webui is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# livemgr-webui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Jardel Weyrich <jweyrich@gmail.com>

# Django settings for webui project.

from tzlocal import get_localzone
import django
import os.path
ROOT = os.path.dirname(os.path.abspath(__file__))

_ = lambda s: s

DEBUG = True

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
# Django 2.0 sets MySQL connections to READ COMMITTED; older versions kept the
# server's default, usually REPEATABLE READ. A server that writes its binary
# log in STATEMENT format then rejects writes to InnoDB tables: switch it to ROW
# or MIXED, or keep the old level in the deployment's DATABASES with
# 'OPTIONS': {'isolation_level': 'repeatable read'}.

# Django 1.11 removes TIME_ZONE = None, which kept the system's time zone. The
# backend stores local times, and the dashboard reads datetime.now(), so name
# the system's zone instead: Django exports TIME_ZONE to the TZ environment
# variable. Where tzlocal can't name it (an /etc/localtime that isn't a link
# and no /etc/timezone), it returns 'local', which Django rejects: set the
# zone's name in the deployment's settings, e.g. TIME_ZONE = 'America/Sao_Paulo'.
TIME_ZONE = get_localzone().zone
# The datetimes stay naive, in TIME_ZONE, as the backend stores them. Django 5.0
# turns time zone support on by default, so keep it off here.
USE_TZ = False

# Language section
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', _('English')),
    ('pt-br', _('Brazilian Portuguese')),
)
USE_I18N = True
# Django 4.0 localizes formatting by default, and deprecates the setting.
if django.VERSION < (4, 0):
    USE_L10N = True
# Django 1.3 deprecates loading translations from the project's locale
# directory implicitly. Listing it here also serves its djangojs catalog.
LOCALE_PATHS = (
    os.path.join(ROOT, 'locale'),
)

MEDIA_ROOT = os.path.join(ROOT, '..', 'media')
MEDIA_URL = '/media/'
# Django 1.4 replaces ADMIN_MEDIA_PREFIX: the admin's files are served
# from STATIC_URL + 'admin/' (django/contrib/admin/static/admin/).
STATIC_URL = '/static/'

# FIXME: ???
SECRET_KEY = '2m74tbo+#7iin(h(nn2d!#=bryc8w*3e9+&7(%g7o5yd*hy-en'

# code config

# Django 1.10 deprecates MIDDLEWARE_CLASSES (old-style middleware) for
# MIDDLEWARE. SessionAuthenticationMiddleware ends a user's other sessions when
# their password changes: opt-in since Django 1.7, and always on from 1.10,
# which leaves the middleware an empty stub.
if django.VERSION >= (1, 10):
    MIDDLEWARE = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    )

ROOT_URLCONF = 'webui.urls'

# Django 3.2 warns (models.W042) about models without an explicit primary key
# unless their type is set here, as a future version changes the default to
# BigAutoField. AutoField is the type migration 0002 records for the backend's
# models: their tables belong to bootstrap/db/create_tables.sql, whatever the
# field's type, and switching it would only add a migration.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Django 1.5's runserver no longer serves the admin's static files by
    # itself (AdminMediaHandler is gone); staticfiles' runserver does, with
    # DEBUG on. The web servers map /static/admin in production.
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_tables2',
    'webui.common',
    'webui.livemgr',
)

# Django 1.8 configures the template engine with TEMPLATES, deprecates the
# TEMPLATE_* settings and moves the context processors out of django.core.
# The engine's debug option follows DEBUG, as TEMPLATE_DEBUG did.
if django.VERSION >= (1, 8):
    TEMPLATES = [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
            ],
        },
    }]
else:
    TEMPLATE_DEBUG = DEBUG
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
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
LOGIN_REDIRECT_URL = '/dashboard'
# Django 1.5 deprecates AUTH_PROFILE_MODULE and User.get_profile(): the
# profile is reached through its one-to-one relation instead (user.profile).
# Django 1.4 hashes passwords with PBKDF2, which Django 1.3 can't read, so SHA1
# stayed the preferred hasher until Django 4.2, which deprecates
# SHA1PasswordHasher: since then PBKDF2 hashes the new passwords, and rewrote a
# SHA1 hash when its account logged in. Django 5.1 removes SHA1PasswordHasher,
# so the accounts whose hash was never rewritten can no longer log in: their
# password is rejected as wrong. List them (add the deployment's --settings),
# then give each a new password with
# "python webui/manage.py changepassword <username>":
#	python webui/manage.py shell -c "from django.contrib.auth.models import User; print(list(User.objects.filter(password__startswith='sha1\$').values_list('username', flat=True)))"
# Django 5.1 also raises PBKDF2's iterations from 720,000 to 870,000: each
# account's hash is rewritten when it next logs in, which logs out that
# account's other sessions once. 5.0 still reads the new hashes.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
# Django 4.1 deprecates CryptPasswordHasher, and 5.0 removes it, as Python 3.13
# removes the crypt module it uses. Django never stored crypt hashes here, but
# accounts whose password was written by hand in that format can no longer log
# in: list them (add the deployment's --settings), then give each a new
# password with "python webui/manage.py changepassword <username>":
#	python webui/manage.py shell -c "from django.contrib.auth.models import User; print(list(User.objects.filter(password__startswith='crypt\$').values_list('username', flat=True)))"
if django.VERSION < (4, 1):
    PASSWORD_HASHERS += ('django.contrib.auth.hashers.CryptPasswordHasher',)

# General stuff
INTERNAL_IPS = ('127.0.0.1', )
CSRF_FAILURE_VIEW = 'webui.livemgr.controllers.profiles.no_cookie'
# Django 4.0 also checks plain HTTP requests against the Origin header that
# browsers send with every POST: it must name the request's scheme and Host. A
# proxy in front of the web UI must pass the Host header through (Apache's
# ProxyPreserveHost On), and one that terminates TLS must say so: set
# SECURE_PROXY_SSL_HEADER in the deployment's settings to the header the proxy
# sets, e.g. ('HTTP_X_FORWARDED_PROTO', 'https'), or list the site's origin in
# CSRF_TRUSTED_ORIGINS, e.g. ['https://livemgr.example.com']. Otherwise every
# form posted, the login's included, lands on CSRF_FAILURE_VIEW.
# Django 1.7 warns that projects started before 1.6 may rely on the old test
# runner. The tests run with settings_test, which sets their runner. Django 1.9
# removes that check.
if django.VERSION < (1, 9):
    SILENCED_SYSTEM_CHECKS = ['1_6.W001']
# Django 1.10 rejects requests with more than 1000 GET/POST parameters. The
# group form posts one per member, so large groups could no longer be saved.
# Request bodies stay capped at DATA_UPLOAD_MAX_MEMORY_SIZE (2.5 MB).
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Sessions
# Django 1.6 serializes sessions as JSON instead of pickle, so they only hold
# JSON values (the messages below and the language code are). Sessions saved
# by an older version fail to decode, which logs those users out once.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
# Logins last 8 hours instead of the default two weeks. Each change to the
# session, such as a flashed message, starts the 8 hours again.
SESSION_COOKIE_AGE = 60 * 60 * 8
# Django 3.1 signs sessions with SHA-256 instead of SHA-1, in a new format. It
# still reads the sessions older versions saved, so upgrading logs no one out,
# but Django 3.0 fails every request (500) whose session 3.1 saved. Before
# rolling back, delete the sessions, which logs everyone out (add the
# deployment's --settings):
#	python webui/manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete()"
# To run 3.0 and 3.1 side by side, set DEFAULT_HASHING_ALGORITHM = 'sha1' in
# the deployment's settings until all run 3.1. Django 4.0 removes it, and no
# longer reads the sessions saved before 3.1: upgrading straight from 3.0 or
# older to 4.0 logs everyone out once.
# Django 2.1 sets the session and CSRF cookies with SameSite=Lax, so browsers
# no longer send them on requests from other sites: a login form posted from
# another site lands on CSRF_FAILURE_VIEW. Set SESSION_COOKIE_SAMESITE and
# CSRF_COOKIE_SAMESITE to None in the deployment's settings to allow it.
# Django 3.0 reads the user's language from the LANGUAGE_COOKIE_NAME cookie
# only, no longer from the session. That cookie ends with the browser session
# by default, but logins last SESSION_COOKIE_AGE: keep it as long.
LANGUAGE_COOKIE_AGE = SESSION_COOKIE_AGE

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
# CA certificate(s) the KeyServer's certificate is verified against. None uses
# the system's trusted CAs.
KEYSERVER_CA_FILE = None
