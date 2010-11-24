# Django settings for webui project.
from webui.settings import *

MIDDLEWARE_CLASSES += (
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
	'debug_toolbar',
)

INTERNAL_IPS += ('10.1.1.16', '192.168.1.100', '192.168.1.101',)

LICENSE_FILE = os.path.join(PROJECT_PATH, 'conf', 'certs', 'cert.pem')
KEYSERVER_HOST = '10.1.1.17'

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
