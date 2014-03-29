from django.db.models import Group, Site, User

#
# SITES
#
#site = Site()
#site.domain = 'livemgr'
#site.name = 'localhost'
#site_livemgr = site.save()
# TODO assert id == 1

#
# GROUPS
#
group = Group()
group.name = 'manager'
group_manager = group.save()

group = Group()
group.name = 'auditor'
group.permissions = [
	'livemgr.see_conversation',
	'livemgr.see_dashboard',
	'livemgr.see_message',
]
group_auditor = group.save()

#
# USERS
#
user = User()
user.username = 'admin'
user.groups.add(group_manager)
user.set_password('admin')
user.is_staff = True
user.is_active = True
user.is_superuser = True
user_admin = user.save()

user = User()
user.username = 'auditor'
user.groups.add(group_auditor)
user.set_password('auditor')
user.is_staff = False
user.is_active = True
user.is_superuser = False
user_auditor = user.save()

#myuser.groups = [group_list]
#myuser.groups.add(group, group, ...)
#myuser.groups.remove(group, group, ...)
#myuser.groups.clear()
#myuser.user_permissions = [permission_list]
#myuser.user_permissions.add(permission, permission, ...)
#myuser.user_permissions.remove(permission, permission, ...)
#myuser.user_permissions.clear()
