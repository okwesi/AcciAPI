from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django.contrib.admin import SimpleListFilter

from .models import Event, EventAmount, EventRegistration


class EventAmountInline(admin.TabularInline):
    model = EventAmount
    extra = 1
    fields = ['amount', 'currency']


class RegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ['user', 'full_name', 'email', 'phone_number', 'gender',
                       'is_church_member', 'church_position', 'nation', 'region',
                       'city_town', 'amount', 'currency', 'is_paid', 'branch']
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False


class EventStatusFilter(SimpleListFilter):
    title = 'Event Status'
    parameter_name = 'event_status'

    def lookups(self, request, model_admin):
        return (
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('past', 'Past'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        now = timezone.now()
        if self.value() == 'upcoming':
            return queryset.filter(start_datetime__gt=now)
        if self.value() == 'ongoing':
            return queryset.filter(start_datetime__lte=now, end_datetime__gte=now)
        if self.value() == 'past':
            return queryset.filter(end_datetime__lt=now)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'start_datetime', 'end_datetime',
                    'registration_count', 'total_amount', 'cover_image_preview']
    list_filter = [EventStatusFilter, 'start_datetime', 'end_datetime']
    search_fields = ['title', 'description', 'location']
    inlines = [EventAmountInline, RegistrationInline]
    date_hierarchy = 'start_datetime'

    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'location', 'cover_image')
        }),
        ('Event Schedule', {
            'fields': ('start_datetime', 'end_datetime')
        }),
    )

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.cover_image.url)
        return "No image"

    cover_image_preview.short_description = 'Cover Image'

    def registration_count(self, obj):
        count = obj.eventregistration_set.count()
        url = reverse('admin:events_eventregistration_changelist') + f'?event__id__exact={obj.id}'
        return format_html('<a href="{}">{} registrations</a>', url, count)

    registration_count.short_description = 'Registrations'

    def total_amount(self, obj):
        total = obj.eventregistration_set.filter(is_paid=True).aggregate(
            total=Sum('amount'))['total'] or 0
        return f"{total:,.2f}"

    total_amount.short_description = 'Total Revenue'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventAmount)
class EventAmountAdmin(admin.ModelAdmin):
    list_display = ['event', 'amount', 'currency']
    list_filter = ['currency']
    search_fields = ['event__title']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['event', 'amount', 'currency']
        return []


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'event', 'email', 'phone_number', 'gender',
                    'church_position', 'amount', 'currency', 'is_paid', 'branch']
    list_filter = ['is_paid', 'gender', 'church_position', 'is_church_member',
                   'event']
    search_fields = ['full_name', 'email', 'phone_number', 'event__title']
    readonly_fields = ['event', 'user', 'full_name', 'email', 'phone_number',
                       'gender', 'is_church_member', 'church_position', 'nation',
                       'region', 'city_town', 'amount', 'currency', 'is_paid', 'branch']
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone_number', 'gender')
        }),
        ('Church Information', {
            'fields': ('is_church_member', 'church_position')
        }),
        ('Location', {
            'fields': ('nation', 'region', 'city_town')
        }),
        ('Payment Information', {
            'fields': ('amount', 'currency', 'is_paid')
        }),
        ('Event Information', {
            'fields': ('event', 'user')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False  # Makes the entire form read-only

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)