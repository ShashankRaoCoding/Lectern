from django.contrib import admin

from .models import Profile, Section, Textbook

admin.site.register(Profile)
admin.site.register(Textbook)
admin.site.register(Section)
