from django.contrib import admin

from .models import Community, CommunityRequest, Initiative, MessageInitiative

admin.site.register(Community)
admin.site.register(CommunityRequest)
admin.site.register(Initiative)
admin.site.register(MessageInitiative)
