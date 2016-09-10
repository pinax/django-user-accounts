import datetime
import pytz

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import (
    TestCase,
    override_settings,
)

from ..models import (
    PasswordExpiry,
    PasswordHistory,
)
from ..utils import check_password_expired


@override_settings(
    ACCOUNT_PASSWORD_USE_HISTORY=True
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
        post_data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": email,
        }
        response = self.client.post(reverse("account_signup"), post_data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email=email)
        self.assertFalse(hasattr(user, "password_expiry"))
        self.assertTrue(hasattr(user, "password_history"))

        # verify password is not expired
        self.assertFalse(check_password_expired(user))

    def test_login_not_expired(self):
        """
        Ensure user can log in successfully without redirect.
        """
        # get login
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("account_login"))
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_login_expired(self):
        """
        Ensure user is redirected to change password if pw is expired.
        """
        # set PasswordHistory timestamp in past so pw is expired.
        self.history.timestamp = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(days=1, seconds=self.expiry.expiry)
        self.history.save()

        # get login
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("account_login"))
        self.assertRedirects(response, reverse("account_password"))

    def test_pw_expiration_reset(self):
        """
        Ensure changing password results in new PasswordHistory.
        """
        qs = PasswordHistory.objects.all()
        self.assertEquals(qs.count(), 1)

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

        qs = PasswordHistory.objects.all()
        self.assertEquals(qs.count(), 2)

        latest = PasswordHistory.objects.latest("timestamp")
        self.assertTrue(latest != self.history)
        self.assertTrue(latest.timestamp > self.history.timestamp)
