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
    # Django 1.5's runserver no longer serves the admin's static files by
    # itself (AdminMediaHandler is gone); staticfiles' runserver does, with
    # DEBUG on. The web servers map /static/admin in production.
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.webdesign',
    'django_tables',
    'webui.common',
    'webui.livemgr',
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
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/dashboard'
# Django 1.5 deprecates AUTH_PROFILE_MODULE and User.get_profile(): the
# profile is reached through its one-to-one relation instead (user.profile).
# Django 1.4 hashes passwords with PBKDF2 and rewrites the stored SHA1 hashes
# on login, which Django 1.3 can't read. Keep SHA1 as the preferred hasher
# until rolling back to 1.3 is no longer an option, then drop this setting.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

# General stuff
INTERNAL_IPS = ('127.0.0.1', )
CSRF_FAILURE_VIEW = 'webui.livemgr.controllers.profiles.no_cookie'

# Sessions
# Django 1.6 serializes sessions as JSON instead of pickle, so they only hold
# JSON values (the messages below and the language code are). Sessions saved
# by an older version fail to decode, which logs those users out once.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

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
