from django.contrib import admin
from apps.shared.models import CustomTypes


@admin.register(CustomTypes)
class CustomTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'category', 'category_name', 'is_active')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    fields = ('name', 'description', 'category', 'category_name', 'is_active')
    readonly_fields = ('id',)
