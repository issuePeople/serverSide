from django.contrib import admin
from . import models


@admin.register(models.Issue)
class Issue(admin.ModelAdmin):
    pass
