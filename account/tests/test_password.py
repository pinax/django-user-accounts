import datetime

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


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "account.auth_backends.EmailAuthenticationBackend"
    ],
    ACCOUNT_PASSWORD_USE_HISTORY=True
)
class PasswordExpirationTestCase(TestCase):

    def setUp(self):
        self.username = "user1"
        self.email = "user1@example.com"
        self.password = "changeme"
        self.user = User.objects.create_user(
            self.email,
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
        Ensure new user has one PasswordExpiry and one PasswordHistory.
        """
        # PasswordExpiry.expiry should be same as ACCOUNT_PASSWORD_EXPIRY
        pass

    def test_login_expired(self):
        """
        Ensure user is redirected to change password if pw is expired.
        """
        # set PasswordHistory timestamp in past so pw is expired.
        self.history.timestamp = datetime.datetime.now() - datetime.timedelta(minutes=2)
        self.history.save()

        # get login
        self.client.login(username=self.email, password=self.password)

        response = self.client.get(reverse("account_login"))
        self.assertRedirects(response, reverse("account_password"))

        # post login
        post_data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(
            reverse("account_login"),
            post_data
        )
        self.assertEquals(response.status_code, 200)

    def test_login_not_expired(self):
        """
        Ensure user logs in successfully without redirect.
        """
        # set PasswordHistory timestamp so pw is not expired.
        # attempt login
        # assert success and user logged in
        pass
