"""
Elite Wealth Capital - Enhanced Django Admin Panel
Full user and financial management with beautiful UI
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
import csv
from .models import CustomUser, ActivityLog, Referral, SiteSettings


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Full-featured user management with financial controls."""
    
    model = CustomUser
    
    list_display = [
        'email', 'full_name', 'balance_display', 'invested_display', 
        'profit_display', 'withdrawn_display', 'account_badge', 
        'kyc_badge', 'status_badge', 'referral_code', 'joined_date'
    ]
    
    list_filter = [
        'is_active', 'is_staff', 'account_type', 'kyc_status', 
        'email_verified', 'two_fa_enabled', 'date_joined'
    ]
    
    search_fields = ['email', 'full_name', 'phone', 'referral_code', 'country']
    ordering = ['-date_joined']
    list_per_page = 30
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('full_name', 'phone', 'country', 'profile_image')}),
        ('FINANCIAL MANAGEMENT - Edit to Add/Remove Funds', {
            'fields': ('balance', 'invested_amount', 'total_profit', 'total_withdrawn', 'referral_bonus'),
            'description': 'Edit these fields directly to adjust user funds. Save to apply.',
        }),
        ('Referral System', {'fields': ('referral_code', 'referred_by')}),
        ('Account Status', {'fields': ('account_type', 'kyc_status')}),
        ('Security Settings', {'fields': ('two_fa_enabled', 'email_verified', 'failed_login_attempts', 'locked_until')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('date_joined', 'last_login')}),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'balance', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'referral_code']
    
    # Import inlines from investments app
    def get_inlines(self, request, obj):
        if obj:  # Only show inlines when editing existing user
            from investments.admin import InvestmentInline, DepositInline, WithdrawalInline
            return [InvestmentInline, DepositInline, WithdrawalInline]
        return []
    
    def balance_display(self, obj):
        balance_value = float(obj.balance)
        balance_color = '#28a745' if balance_value > 0 else '#dc3545' if balance_value < 0 else '#6c757d'
        formatted_currency = '${:,.2f}'.format(balance_value)
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', balance_color, formatted_currency)
    balance_display.short_description = 'Balance'
    balance_display.admin_order_field = 'balance'
    
    def invested_display(self, obj):
        formatted_currency = '${:,.2f}'.format(float(obj.invested_amount))
        return format_html('<span style="color: #007bff;">{}</span>', formatted_currency)
    invested_display.short_description = 'Invested'
    invested_display.admin_order_field = 'invested_amount'
    
    def profit_display(self, obj):
        profit_value = float(obj.total_profit)
        profit_color = '#28a745' if profit_value > 0 else '#6c757d'
        formatted_currency = '${:,.2f}'.format(profit_value)
        return format_html('<span style="color: {};">{}</span>', profit_color, formatted_currency)
    profit_display.short_description = 'Profit'
    profit_display.admin_order_field = 'total_profit'
    
    def withdrawn_display(self, obj):
        formatted_currency = '${:,.2f}'.format(float(obj.total_withdrawn))
        return format_html('<span style="color: #fd7e14;">{}</span>', formatted_currency)
    withdrawn_display.short_description = 'Withdrawn'
    withdrawn_display.admin_order_field = 'total_withdrawn'
    
    def account_badge(self, obj):
        colors = {'beginner': '#6c757d', 'intermediate': '#17a2b8', 'advanced': '#ffc107', 'vip': '#dc3545'}
        return format_html('<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>', colors.get(obj.account_type, '#6c757d'), obj.account_type.upper())
    account_badge.short_description = 'Tier'
    
    def kyc_badge(self, obj):
        colors = {'pending': '#ffc107', 'submitted': '#17a2b8', 'verified': '#28a745', 'rejected': '#dc3545'}
        return format_html('<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>', colors.get(obj.kyc_status, '#6c757d'), obj.kyc_status.upper())
    kyc_badge.short_description = 'KYC'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745;">Active</span>')
        return format_html('<span style="color: #dc3545;">Inactive</span>')
    status_badge.short_description = 'Status'
    
    def joined_date(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d')
    joined_date.short_description = 'Joined'
    
    actions = [
        'activate_users', 'deactivate_users', 'verify_kyc', 'reject_kyc',
        'add_100', 'add_500', 'add_1000', 'add_5000',
        'remove_100', 'remove_500', 'reset_balance',
        'add_profit_50', 'add_profit_100', 'add_profit_500',
        'upgrade_to_vip', 'downgrade_to_beginner', 'verify_email',
        'send_bulk_email', 'export_users_csv'
    ]
    
    @admin.action(description='Export selected users to CSV')
    def export_users_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Full Name', 'Phone', 'Country', 'Balance', 
            'Invested', 'Total Profit', 'Total Withdrawn', 
            'Account Type', 'KYC Status', 'Email Verified',
            'Referral Code', 'Date Joined', 'Last Login', 'Is Active'
        ])
        
        for user in queryset:
            writer.writerow([
                user.email,
                user.full_name,
                user.phone or '',
                user.country or '',
                f'${user.balance:,.2f}',
                f'${user.invested_amount:,.2f}',
                f'${user.total_profit:,.2f}',
                f'${user.total_withdrawn:,.2f}',
                user.account_type,
                user.kyc_status,
                'Yes' if user.email_verified else 'No',
                user.referral_code,
                user.date_joined.strftime('%Y-%m-%d %H:%M'),
                user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'Yes' if user.is_active else 'No'
            ])
        
        self.message_user(request, f'Exported {queryset.count()} users to CSV.')
        return response
    
    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'Activated {queryset.count()} users.')
    
    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {queryset.count()} users.')
    
    @admin.action(description='Verify KYC')
    def verify_kyc(self, request, queryset):
        queryset.update(kyc_status='verified')
        self.message_user(request, f'Verified KYC for {queryset.count()} users.')
    
    @admin.action(description='Reject KYC')
    def reject_kyc(self, request, queryset):
        queryset.update(kyc_status='rejected')
        self.message_user(request, f'Rejected KYC for {queryset.count()} users.')
    
    @admin.action(description='ADD $100 to balance')
    def add_100(self, request, queryset):
        for user in queryset:
            user.balance += Decimal('100.00')
            user.save()
        self.message_user(request, f'Added $100 to {queryset.count()} users.')
    
    @admin.action(description='ADD $500 to balance')
    def add_500(self, request, queryset):
        for user in queryset:
            user.balance += Decimal('500.00')
            user.save()
        self.message_user(request, f'Added $500 to {queryset.count()} users.')
    
    @admin.action(description='ADD $1,000 to balance')
    def add_1000(self, request, queryset):
        for user in queryset:
            user.balance += Decimal('1000.00')
            user.save()
        self.message_user(request, f'Added $1,000 to {queryset.count()} users.')
    
    @admin.action(description='ADD $5,000 to balance')
    def add_5000(self, request, queryset):
        for user in queryset:
            user.balance += Decimal('5000.00')
            user.save()
        self.message_user(request, f'Added $5,000 to {queryset.count()} users.')
    
    @admin.action(description='REMOVE $100 from balance')
    def remove_100(self, request, queryset):
        for user in queryset:
            user.balance = max(Decimal('0'), user.balance - Decimal('100.00'))
            user.save()
        self.message_user(request, f'Removed $100 from {queryset.count()} users.')
    
    @admin.action(description='REMOVE $500 from balance')
    def remove_500(self, request, queryset):
        for user in queryset:
            user.balance = max(Decimal('0'), user.balance - Decimal('500.00'))
            user.save()
        self.message_user(request, f'Removed $500 from {queryset.count()} users.')
    
    @admin.action(description='RESET balance to $0')
    def reset_balance(self, request, queryset):
        queryset.update(balance=Decimal('0'))
        self.message_user(request, f'Reset balance for {queryset.count()} users.')
    
    @admin.action(description='Add $50 profit')
    def add_profit_50(self, request, queryset):
        for user in queryset:
            user.total_profit += Decimal('50.00')
            user.balance += Decimal('50.00')
            user.save()
        self.message_user(request, f'Added $50 profit to {queryset.count()} users.')
    
    @admin.action(description='Add $100 profit')
    def add_profit_100(self, request, queryset):
        for user in queryset:
            user.total_profit += Decimal('100.00')
            user.balance += Decimal('100.00')
            user.save()
        self.message_user(request, f'Added $100 profit to {queryset.count()} users.')
    
    @admin.action(description='Add $500 profit')
    def add_profit_500(self, request, queryset):
        for user in queryset:
            user.total_profit += Decimal('500.00')
            user.balance += Decimal('500.00')
            user.save()
        self.message_user(request, f'Added $500 profit to {queryset.count()} users.')
    
    @admin.action(description='Upgrade to VIP')
    def upgrade_to_vip(self, request, queryset):
        queryset.update(account_type='vip')
        self.message_user(request, f'Upgraded {queryset.count()} users to VIP.')
    
    @admin.action(description='Downgrade to Beginner')
    def downgrade_to_beginner(self, request, queryset):
        queryset.update(account_type='beginner')
        self.message_user(request, f'Downgraded {queryset.count()} users to Beginner.')
    
    @admin.action(description='Verify Email')
    def verify_email(self, request, queryset):
        queryset.update(email_verified=True)
        self.message_user(request, f'Verified email for {queryset.count()} users.')
    
    @admin.action(description='Send bulk email notification')
    def send_bulk_email(self, request, queryset):
        """Send a notification email to selected users."""
        count = 0
        for user in queryset.filter(email_verified=True):
            try:
                send_mail(
                    subject='Important Update from Elite Wealth Capital',
                    message='Dear {},\n\nThis is an important update from Elite Wealth Capital.\n\nBest regards,\nElite Wealth Capital Team'.format(user.full_name or 'Investor'),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                count += 1
            except Exception:
                pass
        self.message_user(request, f'Sent email to {count} users.')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email', 'action', 'description', 'ip_address']
    readonly_fields = ['id', 'user', 'action', 'description', 'ip_address', 'user_agent', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred', 'bonus_display', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['referrer__email', 'referred__email']
    ordering = ['-created_at']
    
    def bonus_display(self, obj):
        return format_html('<span style="color: #28a745; font-weight: bold;">${:,.2f}</span>', obj.bonus_amount)
    bonus_display.short_description = 'Bonus'
    
    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'credited': '#28a745', 'cancelled': '#dc3545'}
        return format_html('<span style="background: {}; color: white; padding: 3px 8px; border-radius: 12px;">{}</span>', colors.get(obj.status, '#6c757d'), obj.status.upper())
    status_badge.short_description = 'Status'
    
    actions = ['credit_bonus', 'cancel_bonus']
    
    @admin.action(description='Credit referral bonus')
    def credit_bonus(self, request, queryset):
        for referral in queryset.filter(status='pending'):
            referral.referrer.referral_bonus += referral.bonus_amount
            referral.referrer.balance += referral.bonus_amount
            referral.referrer.save()
            referral.status = 'credited'
            referral.credited_at = timezone.now()
            referral.save()
        self.message_user(request, 'Bonuses credited successfully.')
    
    @admin.action(description='Cancel referral bonus')
    def cancel_bonus(self, request, queryset):
        queryset.filter(status='pending').update(status='cancelled')
        self.message_user(request, 'Bonuses cancelled.')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Site-wide configuration management."""
    
    list_display = ['site_name', 'company_email', 'maintenance_mode', 'updated_at']
    
    fieldsets = (
        ('🏢 Company Information', {
            'fields': ('site_name', 'site_tagline', 'company_email', 'company_phone', 'company_address'),
            'classes': ('wide',),
        }),
        ('🌐 Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'telegram_url'),
            'classes': ('collapse',),
        }),
        ('💰 Financial Settings', {
            'fields': ('min_deposit', 'max_deposit', 'min_withdrawal', 'max_withdrawal', 'withdrawal_fee_percent'),
            'description': 'Configure deposit and withdrawal limits',
        }),
        ('👥 Referral Program', {
            'fields': ('enable_referrals', 'referral_bonus_percent'),
        }),
        ('🕴️ Agent Program', {
            'fields': ('enable_agent_applications', 'agent_commission_rate'),
        }),
        ('🔒 Security Settings', {
            'fields': ('max_login_attempts', 'lockout_duration_minutes', 'require_email_verification', 'require_kyc_for_withdrawal'),
            'description': 'Security and verification requirements',
        }),
        ('🔧 Maintenance Mode', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'description': 'Enable to show maintenance page to users',
        }),
        ('🔍 SEO Settings', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        ('📝 Homepage Content', {
            'fields': ('hero_title', 'hero_subtitle'),
            'classes': ('collapse',),
        }),
        ('📄 Footer Content', {
            'fields': ('footer_about', 'copyright_text'),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
