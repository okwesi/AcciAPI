from django.contrib import admin
from .models import Donation, Pledge, DonationPayment

class PledgeInline(admin.TabularInline):
    """Inline for displaying Pledges associated with a Donation"""
    model = Pledge
    extra = 0
    readonly_fields = ['user', 'amount', 'currency', 'redeem_date', 'is_redeemed', 'redeemed_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class DonationPaymentInline(admin.TabularInline):
    """Inline for displaying Donation Payments associated with a Pledge or Donation"""
    model = DonationPayment
    extra = 0
    readonly_fields = ['payment_transaction', 'user', 'donation', 'is_pledge', 'pledge', 'donated_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """Admin for Donations - CRUD Enabled"""
    list_display = ['title', 'description']
    fields = ['title', 'description', 'cover_image']
    inlines = [PledgeInline]  # Display pledges inline with donations

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    """Admin for Pledges - Fully Read-Only, Inline to Donations"""
    list_display = ['donation', 'user', 'amount', 'currency', 'redeem_date', 'is_redeemed']
    readonly_fields = ['donation', 'user', 'amount', 'currency', 'redeem_date', 'is_redeemed', 'redeemed_at']
    inlines = [DonationPaymentInline]  # Display payments inline with pledges

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DonationPayment)
class DonationPaymentAdmin(admin.ModelAdmin):
    """Admin for Donation Payments - Fully Read-Only, Inline to Pledges and Donations"""
    list_display = ['user', 'donation', 'is_pledge', 'pledge', 'donated_at']
    readonly_fields = ['payment_transaction', 'user', 'donation', 'is_pledge', 'pledge', 'donated_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
