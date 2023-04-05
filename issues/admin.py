from django.contrib import admin
from . import models


@admin.register(models.Tag)
class Tag(admin.ModelAdmin):
    pass


@admin.register(models.Issue)
class Issue(admin.ModelAdmin):
    pass


@admin.register(models.Attachment)
class Attachment(admin.ModelAdmin):
    pass


@admin.register(models.Comentari)
class Comentari(admin.ModelAdmin):
    pass


@admin.register(models.Log)
class Log(admin.ModelAdmin):
    pass
