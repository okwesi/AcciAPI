from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

from .models import Post, PostMedia, UserInteraction

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1
    readonly_fields = ['file_preview']
    fields = ['file', 'file_type', 'file_preview']

    def file_preview(self, obj):
        if not obj.file:
            return ''
        if obj.file_type == 'image':
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.file.url)
        elif obj.file_type == 'video':
            return format_html('<video width="200" controls><source src="{}" type="video/mp4"></video>', obj.file.url)
        return format_html('<a href="{}">Download {}</a>', obj.file.url, obj.file_type)
    file_preview.short_description = 'Preview'

class InteractionCountFilter(SimpleListFilter):
    title = 'Interaction Count'
    parameter_name = 'interaction_count'

    def lookups(self, request, model_admin):
        return (
            ('high', 'High (>100)'),
            ('medium', 'Medium (20-100)'),
            ('low', 'Low (<20)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.annotate(
                total_interactions=Count('interactions')
            ).filter(total_interactions__gt=100)
        if self.value() == 'medium':
            return queryset.annotate(
                total_interactions=Count('interactions')
            ).filter(total_interactions__range=(20, 100))
        if self.value() == 'low':
            return queryset.annotate(
                total_interactions=Count('interactions')
            ).filter(total_interactions__lt=20)

class UserInteractionInline(admin.TabularInline):
    model = UserInteraction
    extra = 0
    readonly_fields = ['user', 'interaction_type', 'date_created']
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_type', 'created_by',
                   'comments', 'likes', 'shares', 'branch', 'date_created',
                   'media_count', 'is_active']
    list_filter = ['post_type', 'branch', InteractionCountFilter, 'date_created']
    search_fields = ['content', 'created_by__username', 'branch__name']
    readonly_fields = ['comments', 'likes', 'shares', 'date_created']  # Removed 'last_modified'
    inlines = [PostMediaInline, UserInteractionInline]
    actions = ['reset_interaction_counts']
    date_hierarchy = 'date_created'
    list_per_page = 20

    fieldsets = (
        ('Post Information', {
            'fields': ('post_type', 'content', 'branch', 'parent')
        }),
        ('Interaction Metrics', {
            'fields': ('comments', 'likes', 'shares'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'date_created'),  # Removed 'last_modified'
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def media_count(self, obj):
        count = obj.media.count()
        if count > 0:
            url = reverse('admin:content_postmedia_changelist') + f'?post__id__exact={obj.id}'
            return format_html('<a href="{}">{} media files</a>', url, count)
        return '0'
    media_count.short_description = 'Media'

    def view_on_site(self, obj):
        url = reverse('post-detail', args=[obj.id])
        return format_html('<a class="button" href="{}"">View Post</a>', url)
    view_on_site.short_description = 'View'

    def reset_interaction_counts(self, request, queryset):
        queryset.update(comments=0, likes=0, shares=0)
    reset_interaction_counts.short_description = "Reset interaction counts"

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_link', 'file_type', 'file_preview', 'date_created']
    list_filter = ['file_type', 'date_created']
    search_fields = ['post__content', 'file']
    readonly_fields = ['file_preview']

    def post_link(self, obj):
        url = reverse('admin:content_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.post))
    post_link.short_description = 'Post'

    def file_preview(self, obj):
        if not obj.file:
            return ''
        if obj.file_type == 'image':
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.file.url)
        elif obj.file_type == 'video':
            return format_html('<video width="200" controls><source src="{}" type="video/mp4"></video>', obj.file.url)
        return format_html('<a href="{}">Download {}</a>', obj.file.url, obj.file_type)
    file_preview.short_description = 'Preview'

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post_link', 'interaction_type', 'date_created']
    list_filter = ['interaction_type', 'date_created']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['date_created']
    date_hierarchy = 'date_created'

    def post_link(self, obj):
        url = reverse('admin:content_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.post))
    post_link.short_description = 'Post'

    def has_add_permission(self, request):
        return False  # Prevent manual creation of interactions