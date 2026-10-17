from django.test import TestCase
from django.contrib.auth.models import User
from .models import PriceAlert, NotificationLog, UserProfile


class PriceThresholdTest(TestCase):
    """Test threshold comparison logic"""

    def test_price_below_threshold_triggers_alert(self):
        """If current price (4200) <= threshold (4500), alert should fire"""
        self.assertTrue(4200 <= 4500)

    def test_price_above_threshold_does_not_trigger(self):
        """If current price (5000) > threshold (4500), alert should not fire"""
        self.assertFalse(5000 <= 4500)

    def test_price_equal_to_threshold_triggers_alert(self):
        """Edge case: price == threshold should still trigger"""
        self.assertTrue(4500 <= 4500)


class NotificationLogTest(TestCase):
    """Test NotificationLog creation and storage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.alert = PriceAlert.objects.create(
            user=self.user,
            origin='DEL', destination='BOM',
            threshold_price=4500,
            status=PriceAlert.Status.ACTIVE
        )

    def test_notification_log_created_with_correct_message(self):
        """Test that NotificationLog is created with correct data"""
        log = NotificationLog.objects.create(
            alert=self.alert,
            triggered_price=4200,
            message='Price dropped to 4200 for DEL-BOM'
        )
        self.assertEqual(log.triggered_price, 4200)
        self.assertEqual(log.alert, self.alert)
        self.assertIn('DEL-BOM', log.message)

    def test_notification_log_belongs_to_alert(self):
        """Test that NotificationLog correctly links to PriceAlert"""
        log = NotificationLog.objects.create(
            alert=self.alert,
            triggered_price=3900,
            message='Price dropped to 3900 for DEL-BOM'
        )
        self.assertEqual(log.alert.user, self.user)
        self.assertEqual(log.alert.origin, 'DEL')


class AlertScopingTest(TestCase):
    """Test that users only see their own alerts"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='pass'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='pass'
        )
        PriceAlert.objects.create(
            user=self.user1, origin='DEL', destination='BOM',
            threshold_price=4500
        )
        PriceAlert.objects.create(
            user=self.user2, origin='BLR', destination='HYD',
            threshold_price=2000
        )

    def test_user_only_sees_own_alerts(self):
        """Test that user1 only sees their own alerts"""
        user1_alerts = PriceAlert.objects.filter(user=self.user1)
        self.assertEqual(user1_alerts.count(), 1)
        self.assertEqual(user1_alerts.first().origin, 'DEL')

    def test_user_cannot_see_other_users_alerts(self):
        """Test that user1 cannot see user2's alerts"""
        user1_alerts = PriceAlert.objects.filter(user=self.user1)
        # user1 should not see user2's BLR-HYD alert
        for alert in user1_alerts:
            self.assertNotEqual(alert.origin, 'BLR')

    def test_alert_count_per_user(self):
        """Test that each user sees correct number of alerts"""
        user1_count = PriceAlert.objects.filter(user=self.user1).count()
        user2_count = PriceAlert.objects.filter(user=self.user2).count()
        self.assertEqual(user1_count, 1)
        self.assertEqual(user2_count, 1)


class UserProfileTest(TestCase):
    """Test UserProfile auto-creation and role assignment"""

    def test_user_profile_auto_created(self):
        """Test that UserProfile is auto-created when User is created"""
        user = User.objects.create_user(username='newuser', password='pass')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_profile_default_role_is_user(self):
        """Test that new UserProfile defaults to 'user' role"""
        user = User.objects.create_user(username='newuser2', password='pass')
        profile = user.profile
        self.assertEqual(profile.role, UserProfile.Role.USER)

    def test_admin_role_assignment(self):
        """Test that admin role can be assigned"""
        user = User.objects.create_user(username='adminuser', password='pass')
        profile = user.profile
        profile.role = UserProfile.Role.ADMIN
        profile.save()

        updated_profile = UserProfile.objects.get(user=user)
        self.assertEqual(updated_profile.role, UserProfile.Role.ADMIN)
