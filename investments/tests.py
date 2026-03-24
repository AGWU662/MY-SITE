from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from investments.models import Deposit

User = get_user_model()


class InvestmentModelPropertiesTests(TestCase):
    """Tests for Investment model computed properties."""

    def setUp(self):
        from investments.models import InvestmentPlan, Investment

        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
        )
        self.plan = InvestmentPlan.objects.create(
            name='Test Plan',
            min_amount=Decimal('100.00'),
            max_amount=Decimal('10000.00'),
            daily_roi=Decimal('1.00'),
            duration_days=30,
            is_active=True,
        )
        now = timezone.now()
        inv = Investment.objects.create(
            user=self.user,
            plan=self.plan,
            amount=Decimal('500.00'),
            end_date=now + timedelta(days=20),
            expected_profit=Decimal('150.00'),
            status='active',
        )
        # start_date has auto_now_add=True — backdate via update() to simulate
        # a 10-day-old investment for elapsed/progress arithmetic tests.
        Investment.objects.filter(pk=inv.pk).update(
            start_date=now - timedelta(days=10)
        )
        self.investment = Investment.objects.get(pk=inv.pk)

    def test_maturity_date_equals_end_date(self):
        """maturity_date property should be an alias for end_date."""
        self.assertEqual(self.investment.maturity_date, self.investment.end_date)

    def test_duration_days(self):
        """duration_days should return the total days between start and end."""
        self.assertEqual(self.investment.duration_days, 30)

    def test_days_elapsed_within_expected_range(self):
        """days_elapsed should be approximately 10 (clamped to [0, duration_days])."""
        elapsed = self.investment.days_elapsed
        # Allow a 2-day window in case the test runs near midnight
        self.assertGreaterEqual(elapsed, 9)
        self.assertLessEqual(elapsed, 11)

    def test_progress_percentage_within_range(self):
        """progress_percentage should be between 0 and 100."""
        pct = self.investment.progress_percentage
        self.assertGreaterEqual(pct, 0)
        self.assertLessEqual(pct, 100)

    def test_progress_percentage_approximately_correct(self):
        """With 10/30 days elapsed, progress should be about 33%."""
        pct = self.investment.progress_percentage
        # 10 days out of 30 => ~33%; allow ±5% tolerance for timing
        self.assertAlmostEqual(pct, 33.33, delta=5)

    def test_days_remaining(self):
        """days_remaining should be non-negative and within duration."""
        remaining = self.investment.days_remaining
        self.assertGreaterEqual(remaining, 0)
        self.assertLessEqual(remaining, 30)

    def test_is_matured_false_for_active(self):
        """Active investment with future end_date should not be matured."""
        self.assertFalse(self.investment.is_matured())

    def test_is_matured_true_for_past_end_date(self):
        """Investment with past end_date should be matured."""
        self.investment.end_date = timezone.now() - timedelta(days=1)
        self.assertTrue(self.investment.is_matured())


class DepositMinimumTests(TestCase):
    """Tests to verify minimum deposit is set to $30."""

    def test_settings_min_deposit_is_30(self):
        """MIN_DEPOSIT in settings should be 30."""
        from django.conf import settings
        self.assertEqual(getattr(settings, 'MIN_DEPOSIT', None), 30)

    def test_site_settings_min_deposit_default_is_30(self):
        """SiteSettings model default for min_deposit should be 30."""
        from accounts.site_settings import SiteSettings
        field = SiteSettings._meta.get_field('min_deposit')
        self.assertEqual(field.default, 30)

    def test_deposit_view_rejects_below_minimum(self):
        """Deposit view should reject amounts below $30 and redirect back to add_funds."""
        from django.test import Client
        from django.urls import reverse

        user = User.objects.create_user(email='dep@example.com', password='TestPass123!')
        client = Client()
        client.force_login(user)

        response = client.post(reverse('add_funds'), {
            'amount': '20',
            'crypto_type': 'USDT',
        })

        # Should redirect back to add_funds (error), not to deposit_status
        self.assertEqual(response.status_code, 302)
        self.assertIn('add-funds', response['Location'])

    def test_deposit_view_accepts_at_minimum(self):
        """Deposit view should accept amounts of exactly $30 and create a Deposit record."""
        from django.test import Client
        from django.urls import reverse
        from investments.models import Deposit

        user = User.objects.create_user(email='dep2@example.com', password='TestPass123!')
        client = Client()
        client.force_login(user)

        response = client.post(reverse('add_funds'), {
            'amount': '30',
            'crypto_type': 'USDT',
        })

        # Should redirect to deposit_status (success), not back to add_funds (error)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('/add-funds/', response['Location'])
        self.assertEqual(Deposit.objects.filter(user=user, amount=Decimal('30')).count(), 1)



class DepositCryptoTypeValidationTests(TestCase):
    """Tests that deposit submissions correctly handle crypto_type case."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='depositor@example.com',
            password='TestPass123!',
            full_name='Depositor User',
        )
        self.client.login(username='depositor@example.com', password='TestPass123!')

    def test_deposit_with_uppercase_crypto_type_succeeds(self):
        """Uppercase crypto_type (as sent by corrected JS) should be accepted."""
        response = self.client.post(reverse('add_funds'), {
            'amount': '100.00',
            'crypto_type': 'BTC',
        })
        # Should redirect to deposit_status (successful deposit creation)
        self.assertIn(response.status_code, [301, 302])
        self.assertTrue(Deposit.objects.filter(user=self.user, crypto_type='BTC').exists())

    def test_deposit_with_lowercase_crypto_type_fails(self):
        """Lowercase crypto_type (old broken JS behavior) should be rejected."""
        response = self.client.post(reverse('add_funds'), {
            'amount': '100.00',
            'crypto_type': 'btc',   # lowercase — old broken behavior
        })
        # Should not create a deposit with this invalid type
        self.assertFalse(Deposit.objects.filter(user=self.user, crypto_type='btc').exists())
        # Should redirect back (either to add_funds or stay on page with error)
        self.assertIn(response.status_code, [200, 301, 302])

    def test_deposit_with_tx_hash_stored(self):
        """tx_hash submitted in form should be saved on the Deposit."""
        response = self.client.post(reverse('add_funds'), {
            'amount': '50.00',
            'crypto_type': 'USDT',
            'tx_hash': 'abc123txhashvalue',
        })
        dep = Deposit.objects.filter(user=self.user, crypto_type='USDT').first()
        self.assertIsNotNone(dep)
        self.assertEqual(dep.tx_hash, 'abc123txhashvalue')

    def test_deposit_below_minimum_rejected(self):
        """Deposits below the minimum should be rejected."""
        response = self.client.post(reverse('add_funds'), {
            'amount': '5.00',
            'crypto_type': 'BTC',
        })
        # Should not create a deposit
        self.assertFalse(Deposit.objects.filter(user=self.user).exists())
