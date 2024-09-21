from django.contrib import admin

from .models import Branch, Area, District


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch_head', 'district', 'is_active', 'date_created')
    list_display_links = list_display
    search_fields = ('name', 'branch_head', 'address')
    list_filter = ('district',)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'area_head', 'is_active', 'date_created')
    list_display_links = list_display
    search_fields = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'district_head', 'area','is_active', 'date_created')
    list_display_links = list_display
    search_fields = ('name', 'district_head')
