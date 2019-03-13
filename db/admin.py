from django.contrib import admin

from .models import Email, Header, Body, Attachment, Host, IPAddress, EmailAddress, Url, Analysis

admin.site.register(Email)
admin.site.register(Header)
admin.site.register(Body)
admin.site.register(Attachment)

admin.site.register(Host)
admin.site.register(IPAddress)
admin.site.register(EmailAddress)
admin.site.register(Url)

admin.site.register(Analysis)
