from django.contrib import admin

from .models import LLMModel, Provider

admin.site.register(Provider)
admin.site.register(LLMModel)
