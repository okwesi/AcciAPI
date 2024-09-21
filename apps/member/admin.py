from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'id', 'email', 'first_name', 'last_name', 'gender', 'marital_status', 'branch')
    list_filter = ('gender', 'marital_status', 'branch')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'phone_number', 'first_name', 'last_name', 'other_name')
        }),
        ('Contact Information', {
            'fields': ('address', 'emergency_contact_name', 'emergency_contact_phone_number')
        }),
        ('Demographic Information', {
            'fields': ('gender', 'date_of_birth', 'hometown', 'region', 'country')
        }),
        ('Marital Status & Education', {
            'fields': ('marital_status', 'educational_level')
        }),
        ('Church Information', {
            'fields': ('branch', 'is_baptised', 'date_joined', 'communication_preferences', 'occupation')
        }),
        ('Membership Information', {
            'fields': ('member_title', 'member_type', 'member_position', 'member_group')
        }),
        ('Base Information', {
            'fields': ('is_active', 'created_by', 'modified_by', 'deleted_by')
        }),
    )
