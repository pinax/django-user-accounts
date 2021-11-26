import datetime

import django
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.test import TestCase, modify_settings, override_settings
from django.urls import reverse

import pytz

from ..models import PasswordExpiry, PasswordHistory
from ..utils import check_password_expired


def middleware_kwarg(value):
    if django.VERSION >= (1, 10):
        kwarg = "MIDDLEWARE"
    else:
        kwarg = "MIDDLEWARE_CLASSES"
    return {kwarg: value}


@override_settings(
    ACCOUNT_PASSWORD_USE_HISTORY=True
)
@modify_settings(
    **middleware_kwarg({
        "append": "account.middleware.ExpiredPasswordMiddleware"
    })
)
class PasswordExpirationTestCase(TestCase):

    def setUp(self):
        self.username = "user1"
        self.email = "user1@example.com"
        self.password = "changeme"
        self.user = User.objects.create_user(
            self.username,
            email=self.email,
            password=self.password,
        )
        # create PasswordExpiry for user
        self.expiry = PasswordExpiry.objects.create(
            user=self.user,
            expiry=60,  # password expires after sixty seconds
        )
        # create PasswordHistory for user
        self.history = PasswordHistory.objects.create(
            user=self.user,
            password=make_password(self.password)
        )

    def test_signup(self):
        """
        Ensure new user has one PasswordHistory and no PasswordExpiry.
        """
        email = "foobar@example.com"
        password = "bar"
        post_data = {
            "username": "foo",
            "password": password,
            "password_confirm": password,
            "email": email,
        }
        response = self.client.post(reverse("account_signup"), post_data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email=email)
        self.assertFalse(hasattr(user, "password_expiry"))
        latest_history = user.password_history.latest("timestamp")
        self.assertTrue(latest_history)

        # verify password is not expired
        self.assertFalse(check_password_expired(user))
        # verify raw password matches encrypted password in history
        self.assertTrue(check_password(password, latest_history.password))

    def test_get_not_expired(self):
        """
        Ensure authenticated user can retrieve account settings page
        without "password change" redirect.
        """
        self.client.login(username=self.username, password=self.password)

        # get account settings page (could be any application page)
        response = self.client.get(reverse("account_settings"))
        self.assertEquals(response.status_code, 200)

    def test_get_expired(self):
        """
        Ensure authenticated user is redirected to change password
        when retrieving account settings page if password is expired.
        """
        # set PasswordHistory timestamp in past so password is expired.
        self.history.timestamp = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(days=1, seconds=self.expiry.expiry)
        self.history.save()

        self.client.login(username=self.username, password=self.password)

        # get account settings page (could be any application page)
        url_name = "account_settings"
        response = self.client.get(reverse(url_name))

        # verify desired page is set as "?next=" in redirect URL
        redirect_url = "{}?next={}".format(reverse("account_password"), url_name)
        self.assertRedirects(response, redirect_url)

    def test_password_expiration_reset(self):
        """
        Ensure changing password results in new PasswordHistory.
        """
        history_count = self.user.password_history.count()

        # get login
        self.client.login(username=self.username, password=self.password)

        # post new password to reset PasswordHistory
        new_password = "lynyrdskynyrd"
        post_data = {
            "password_current": self.password,
            "password_new": new_password,
            "password_new_confirm": new_password,
        }
        self.client.post(
            reverse("account_password"),
            post_data
        )
        # Should see one more history entry for this user
        self.assertEquals(self.user.password_history.count(), history_count + 1)

        latest = PasswordHistory.objects.latest("timestamp")
        self.assertTrue(latest != self.history)
        self.assertTrue(latest.timestamp > self.history.timestamp)


@modify_settings(
    **middleware_kwarg({
        "append": "account.middleware.ExpiredPasswordMiddleware"
    })
)
class ExistingUserNoHistoryTestCase(TestCase):
    """
    Tests where user has no PasswordHistory.
    """

    def setUp(self):
        self.username = "user1"
        self.email = "user1@example.com"
        self.password = "changeme"
        self.user = User.objects.create_user(
            self.username,
            email=self.email,
            password=self.password,
        )

    def test_get_no_history(self):
        """
        Ensure authenticated user without password history can retrieve
        account settings page without "password change" redirect.
        """
        self.client.login(username=self.username, password=self.password)

        with override_settings(
            ACCOUNT_PASSWORD_USE_HISTORY=True
        ):
            # get account settings page (could be any application page)
            response = self.client.get(reverse("account_settings"))
            self.assertEquals(response.status_code, 200)

    def test_password_expiration_reset(self):
        """
        Ensure changing password results in new PasswordHistory,
        even when no PasswordHistory exists.
        """
        history_count = self.user.password_history.count()

        # get login
        self.client.login(username=self.username, password=self.password)

        # post new password to reset PasswordHistory
        new_password = "lynyrdskynyrd"
        post_data = {
            "password_current": self.password,
            "password_new": new_password,
            "password_new_confirm": new_password,
        }
        with override_settings(
            ACCOUNT_PASSWORD_USE_HISTORY=True
        ):
            self.client.post(
                reverse("account_password"),
                post_data
            )
            # Should see one more history entry for this user
            self.assertEquals(self.user.password_history.count(), history_count + 1)

    def test_password_reset(self):
        """
        Ensure changing password results in NO new PasswordHistory
        when ACCOUNT_PASSWORD_USE_HISTORY == False.
        """
        # get login
        self.client.login(username=self.username, password=self.password)

        # post new password to reset PasswordHistory
        new_password = "lynyrdskynyrd"
        post_data = {
            "password_current": self.password,
            "password_new": new_password,
            "password_new_confirm": new_password,
        }
        with override_settings(
            ACCOUNT_PASSWORD_USE_HISTORY=False
        ):
            self.client.post(
                reverse("account_password"),
                post_data
            )
            # history count should be zero
            self.assertEquals(self.user.password_history.count(), 0)
