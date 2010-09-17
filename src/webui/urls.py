from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from webui import settings

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

#handler404 = 'django.views.defaults.page_not_found'
#handler500 = 'django.views.defaults.server_error'
handler404 = 'webui.controllers.handlers.error_404'
handler500 = 'webui.controllers.handlers.error_500'

urlpatterns = patterns('',
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/(.*)', admin.site.root),

	# Internationalization
	(r'^i18n/', include('django.conf.urls.i18n')),
	(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('webui',),}),

	# User defined
	(r'^media/(?P<path>.*)$', 'django.views.static.serve',
		{ 'document_root': settings.MEDIA_ROOT }),
	#(r'^', include('improj.imdata.urls',
	#	namespace='improj', app_name='imdata')),
	(r'^', include('webui.imdata.urls',
		namespace='webui', app_name='imdata')),
)
