"""
Custom admin configuration for SmartGriev
Unregisters models that should not be directly managed through admin interface
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

# Unregister Groups - not using Django group permissions
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Unregister Token Blacklist models - system managed, no manual intervention needed
try:
    admin.site.unregister(OutstandingToken)
    admin.site.unregister(BlacklistedToken)
except admin.sites.NotRegistered:
    pass

# Customize admin site header and title
admin.site.site_header = "SmartGriev Administration"
admin.site.site_title = "SmartGriev Admin Portal"
admin.site.index_title = "Welcome to SmartGriev Administration"
