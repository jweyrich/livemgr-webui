from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views
from webui.livemgr.controllers import profiles, settings, acls, badwords, \
	conversations, groups, users, buddies, dashboard, license

urlpatterns = patterns('webui.livemgr.controllers',
	url(r'^$', dashboard.index, name='index'),
	# Dashboard
	url(r'^dashboard/$', dashboard.index, name='dashboard-index'),
	url(r'^dashboard/query/$', dashboard.query, name='dashboard-query'),
	# Acls
	url(r'^acls/$', acls.index, name='acls-index'),
	url(r'^acls/add/$', acls.add, name='acls-add'),
	url(r'^acls/delete/$', acls.delete_many, name='acls-delete-many'),
	url(r'^acls/(?P<object_id>\d+)/$', acls.edit, name='acls-edit'),
	url(r'^acls/(?P<object_id>\d+)/delete/$', acls.delete, name='acls-delete'),
	# Users
	url(r'^users/$', users.index, name='users-index'),
	url(r'^users/add/$', users.add, name='users-add'),
	url(r'^users/(?P<object_id>\d+)/$', users.edit, name='users-edit'),
	url(r'^users/(?P<object_id>\d+)/delete/$', users.delete, name='users-delete'),
#	url(r'^users/delete/$', users.delete_many, name='users-delete-many'),
	# Buddies
	url(r'^users/(?P<user_id>\d+)/contacts/$', buddies.index, name='buddies-index'),
	url(r'^users/(?P<user_id>\d+)/block/$', buddies.block, name='buddies-block-many'),
	url(r'^users/(?P<user_id>\d+)/unblock/$', buddies.unblock, name='buddies-unblock-many'),
	# Groups
	url(r'^groups/$', groups.index, name='groups-index'),
	url(r'^groups/add/$', groups.add, name='groups-add'),
	url(r'^groups/delete/$', groups.delete_many, name='groups-delete-many'),
	url(r'^groups/(?P<object_id>\d+)/$', groups.edit, name='groups-edit'),
	url(r'^groups/(?P<object_id>\d+)/delete/$', groups.delete, name='groups-delete'),
	# Conversations
	url(r'^conversations/$', conversations.index, name='conversations-index'),
	url(r'^conversations/(?P<object_id>\d+)/$', conversations.show, name='conversations-show'),
	url(r'^conversations/(?P<object_id>\d+)/report/pdf/$', conversations.report_pdf, name='conversations-report-pdf'),
	# Badwords
	url(r'^badwords/$', badwords.index, name='badwords-index'),
	url(r'^badwords/add/$', badwords.add, name='badwords-add'),
	url(r'^badwords/delete/$', badwords.delete_many, name='badwords-delete-many'),
	url(r'^badwords/disable/$', badwords.disable_many, name='badwords-disable-many'),
	url(r'^badwords/enable/$', badwords.enable_many, name='badwords-enable-many'),
	url(r'^badwords/(?P<object_id>\d+)/$', badwords.edit, name='badwords-edit'),
	url(r'^badwords/(?P<object_id>\d+)/delete/$', badwords.delete, name='badwords-delete'),
	# Settings
	url(r'^settings/$', settings.update, name='settings-update'),
	# License
	url(r'^license/$', license.index, name='license-index'),
	url(r'^license/edit/$', license.edit, name='license-edit'),
	# Profiles
	url(r'^login/$', profiles.login,
		{'template_name': 'profiles/login.html'},
		name='profiles-login'),
#	url(r'^profiles/login/$', views.login,
#		{'template_name': 'profiles/login.html'},
#		name='profiles-login'),
	url(r'^logout/$', views.logout_then_login,
		{'login_url': '/login/'},
		name='profiles-logout'),
	url(r'^profile/update/$', profiles.update, name='profiles-update'),
#	url(r'^profiles/$', profiles.index, name='profiles-index'),
)
