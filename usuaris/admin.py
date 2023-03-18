from django.contrib import admin
from . import models


@admin.register(models.Usuari)
class Usuari(admin.ModelAdmin):
    pass
