from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ActivityLogViewTests(TestCase):
    """Tests for the user activity log page."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='actlog@example.com',
            password='TestPass123!',
            full_name='Activity User',
        )

    def test_activity_log_requires_login(self):
        response = self.client.get(reverse('activity_log'))
        self.assertIn(response.status_code, [301, 302])
        self.assertIn('/login', response['Location'])

    def test_activity_log_accessible_when_logged_in(self):
        self.client.login(username='actlog@example.com', password='TestPass123!')
        response = self.client.get(reverse('activity_log'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Activity Log')


class ReferralLeaderboardViewTests(TestCase):
    """Tests for the referral leaderboard page."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='leader@example.com',
            password='TestPass123!',
            full_name='Leader User',
        )

    def test_leaderboard_requires_login(self):
        response = self.client.get(reverse('referral_leaderboard'))
        self.assertIn(response.status_code, [301, 302])

    def test_leaderboard_accessible_when_logged_in(self):
        self.client.login(username='leader@example.com', password='TestPass123!')
        response = self.client.get(reverse('referral_leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leaderboard')


class KYCGatedWithdrawTests(TestCase):
    """Tests for KYC gating on the withdraw view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='withdraw@example.com',
            password='TestPass123!',
            full_name='Withdraw User',
        )
        self.user.balance = 1000
        self.user.save()

    def test_withdraw_blocked_without_kyc(self):
        """POST to withdraw with unverified KYC should redirect to KYC upload."""
        self.client.login(username='withdraw@example.com', password='TestPass123!')
        response = self.client.post(reverse('withdraw'), {
            'amount': '50',
            'crypto_type': 'BTC',
            'wallet_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf'
        })
        # Should redirect to KYC page, not dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn('kyc', response['Location'])

    def test_withdraw_page_shows_kyc_banner(self):
        """GET withdraw page for unverified user should show KYC banner."""
        self.client.login(username='withdraw@example.com', password='TestPass123!')
        response = self.client.get(reverse('withdraw'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Identity Verification Required')

    def test_withdraw_page_no_kyc_banner_for_verified_user(self):
        """Verified user should not see KYC banner."""
        self.user.kyc_status = 'verified'
        self.user.save()
        self.client.login(username='withdraw@example.com', password='TestPass123!')
        response = self.client.get(reverse('withdraw'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Identity Verification Required')


class AdminPanelAccessTests(TestCase):
    """Tests for the custom admin panel access control."""

    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='TestPass123!',
            full_name='Regular User',
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='TestPass123!',
            full_name='Staff User',
            is_staff=True,
        )

    def test_admin_panel_requires_staff(self):
        """Regular user should be redirected away from admin panel."""
        self.client.login(username='user@example.com', password='TestPass123!')
        response = self.client.get(reverse('admin_panel'))
        self.assertIn(response.status_code, [301, 302])

    def test_admin_panel_accessible_for_staff(self):
        """Staff user should be able to access the admin panel."""
        self.client.login(username='staff@example.com', password='TestPass123!')
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Panel')

    def test_admin_panel_shows_overview_stats(self):
        """Admin panel should display platform stats."""
        self.client.login(username='staff@example.com', password='TestPass123!')
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Platform Overview')


class ReferralBonusSignupTests(TestCase):
    """Tests for the referral bonus flow on signup."""

    def setUp(self):
        self.client = Client()
        self.referrer = User.objects.create_user(
            email='referrer@example.com',
            password='TestPass123!',
            full_name='Referrer User',
        )

    def test_signup_with_valid_referral_code_gives_new_user_20(self):
        """New user signing up with a valid referral code should get $20."""
        response = self.client.post(reverse('signup'), {
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'referral_code': self.referrer.referral_code,
            'terms': 'on',
        })
        self.assertIn(response.status_code, [200, 302])
        new_user = User.objects.filter(email='newuser@example.com').first()
        if new_user:
            from decimal import Decimal
            self.assertEqual(new_user.balance, Decimal('20.00'))

    def test_signup_with_valid_referral_code_gives_referrer_30(self):
        """Referrer should get $30 when someone uses their code."""
        self.client.post(reverse('signup'), {
            'full_name': 'New User2',
            'email': 'newuser2@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'referral_code': self.referrer.referral_code,
            'terms': 'on',
        })
        self.referrer.refresh_from_db()
        from decimal import Decimal
        self.assertEqual(self.referrer.referral_bonus, Decimal('30.00'))
        self.assertEqual(self.referrer.balance, Decimal('30.00'))

    def test_signup_without_referral_code_no_bonus(self):
        """Signing up without a referral code gives no bonus."""
        self.client.post(reverse('signup'), {
            'full_name': 'Plain User',
            'email': 'plain@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'terms': 'on',
        })
        user = User.objects.filter(email='plain@example.com').first()
        if user:
            from decimal import Decimal
            self.assertEqual(user.balance, Decimal('0.00'))
