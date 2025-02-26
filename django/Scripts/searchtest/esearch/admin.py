from django.contrib import admin
from esearch.models import TempData
# Register your models here.
@admin.register(TempData)
class TempDataAdmin(admin.ModelAdmin):
    list_display = ("fileName", "jsonContent")