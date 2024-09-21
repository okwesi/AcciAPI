from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.html import format_html

from apps.accounts.models import GroupRank
from acci.settings.base import ENVIRONMENT

User = get_user_model()




@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # List columns to display on the User model listing page
    list_display = ('id', 'first_name', 'last_name', 'verification_code',
                    'date_created')
    list_display_links = list_display

    # Enable search functionality based on specific fields
    search_fields = ('first_name', 'last_name', 'email')

    # Enable filtering based on gender
    list_filter = ('gender',)

    # Specify which fields are readonly in the admin interface
    readonly_fields = ('id',)

    # Specify which fields to display in the User details form
    fieldsets = (('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'branch')}),
                 ('Contact Info', {'fields': ('email', 'phone_number')}),
                 ('Other', {'fields': ('verification_code',)}),)


class GroupRankInline(admin.TabularInline):
    model = GroupRank
    extra = 0  # Number of empty forms to display
    readonly_fields = ['date_created', 'date_modified', 'created_by', 'date_deleted', 'deleted_by',
                       'is_active']  # Fields from BaseModel


class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_rank', 'get_is_default', 'get_is_active']
    list_display_links = list_display
    ordering = 'ranking__rank', 'ranking__is_default',

    def get_rank(self, obj):
        return obj.ranking.rank if hasattr(obj, 'ranking') else None

    get_rank.admin_order_field = 'ranking__rank'  # Allow sorting by 'rank'
    get_rank.short_description = 'Rank'

    def get_is_default(self, obj):
        return obj.ranking.is_default if hasattr(obj, 'ranking') else None

    get_is_default.admin_order_field = 'ranking__is_default'  # Allow sorting by 'is_default'
    get_is_default.short_description = 'Is Default'

    def get_is_active(self, obj):
        return obj.ranking.is_active if hasattr(obj, 'ranking') else None

    get_is_active.short_description = 'Is Active'

    inlines = [GroupRankInline]  # Include GroupRank fields as inline

    filter_horizontal = ['permissions']  # Display permissions as a horizontal filter


# Unregister the original Group admin and then register the custom one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
env_mapping = {
    'local': 'Local',
    'staging': 'Dev',
    'production': 'Live'
}
env_alias = env_mapping[ENVIRONMENT]
admin.site.site_header = f'Scanport Backend - {env_alias}'
admin.site.site_title = f'Scanport Backend - {env_alias}'
admin.site.index_title = f'Scanport Backend Admin - {env_alias}'



