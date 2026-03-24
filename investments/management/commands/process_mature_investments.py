"""
Management command to process mature investments.
Run this command periodically (e.g., every hour via cron) to:
1. Find all active investments that have reached maturity
2. Credit the user's balance with investment amount + profit
3. Update investment status to completed
4. Create notification for the user

Usage:
    python manage.py process_mature_investments
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from investments.models import Investment
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Process all mature investments and credit profits to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be processed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find all active investments that have matured
        now = timezone.now()
        mature_investments = Investment.objects.filter(
            status='active',
            end_date__lte=now
        ).select_related('user', 'plan')
        
        count = mature_investments.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No mature investments to process'))
            return
        
        self.stdout.write(f'Found {count} mature investment(s) to process')
        
        processed = 0
        failed = 0
        
        for investment in mature_investments:
            try:
                if dry_run:
                    self._preview_investment(investment)
                else:
                    self._process_investment(investment)
                processed += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to process investment {investment.id}: {str(e)}')
                )
                failed += 1
        
        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'Would process: {processed} investment(s)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully processed: {processed} investment(s)'))
        
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'Failed: {failed} investment(s)'))

    def _preview_investment(self, investment):
        """Preview what would happen without making changes."""
        user = investment.user
        total_payout = investment.amount + investment.expected_profit
        
        self.stdout.write(
            f'  [PREVIEW] Investment {str(investment.id)[:8]}...\n'
            f'    User: {user.email}\n'
            f'    Plan: {investment.plan.name}\n'
            f'    Amount: ${investment.amount:,.2f}\n'
            f'    Profit: ${investment.expected_profit:,.2f}\n'
            f'    Total Payout: ${total_payout:,.2f}\n'
            f'    User Balance: ${user.balance:,.2f} → ${(user.balance + total_payout):,.2f}'
        )

    @transaction.atomic
    def _process_investment(self, investment):
        """Process a single mature investment."""
        user = investment.user
        
        # Calculate total payout (investment amount + profit)
        total_payout = investment.amount + investment.expected_profit
        
        self.stdout.write(
            f'Processing investment {str(investment.id)[:8]}... '
            f'(User: {user.email}, Amount: ${investment.amount:,.2f}, Profit: ${investment.expected_profit:,.2f})'
        )
        
        # Lock user row for update
        user = type(user).objects.select_for_update().get(pk=user.pk)
        
        # Credit user balance
        user.balance = user.balance + total_payout
        user.total_profit = user.total_profit + investment.expected_profit
        user.save(update_fields=['balance', 'total_profit'])
        
        # Update investment status
        investment.status = 'completed'
        investment.actual_profit = investment.expected_profit
        investment.completed_at = timezone.now()
        investment.save(update_fields=['status', 'actual_profit', 'completed_at'])
        
        # Create notification for user
        Notification.objects.create(
            user=user,
            title='Investment Completed! 🎉',
            message=(
                f'Your investment of ${investment.amount:,.2f} in {investment.plan.name} has matured! '
                f'${total_payout:,.2f} (including ${investment.expected_profit:,.2f} profit) '
                f'has been credited to your account balance.'
            ),
            notification_type='investment'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Credited ${total_payout:,.2f} to {user.email}')
        )
