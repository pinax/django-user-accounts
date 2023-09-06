from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase, override_settings


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "account.auth_backends.UsernameAuthenticationBackend"
    ]
)
class UsernameAuthenticationBackendTestCase(TestCase):

    def create_user(self, username, email, password):
        user = User.objects.create_user(username, email=email, password=password)
        return user

    def test_successful_auth(self):
        created_user = self.create_user("user1", "user1@example.com", "password")
        authed_user = authenticate(username="user1", password="password")
        self.assertTrue(authed_user is not None)
        self.assertEqual(created_user.pk, authed_user.pk)

    def test_unsuccessful_auth(self):
        authed_user = authenticate(username="user-does-not-exist", password="password")
        self.assertTrue(authed_user is None)

    def test_missing_credentials(self):
        self.create_user("user1", "user1@example.com", "password")
        self.assertTrue(authenticate() is None)
        self.assertTrue(authenticate(username="user1") is None)

    def test_successful_auth_django_2_1(self):
        created_user = self.create_user("user1", "user1@example.com", "password")
        request = None
        authed_user = authenticate(request, username="user1", password="password")
        self.assertTrue(authed_user is not None)
        self.assertEqual(created_user.pk, authed_user.pk)

    def test_unsuccessful_auth_django_2_1(self):
        request = None
        authed_user = authenticate(request, username="user-does-not-exist", password="password")
        self.assertTrue(authed_user is None)


@override_settings(
    AUTHENTICATION_BACKENDS=[
        "account.auth_backends.EmailAuthenticationBackend"
    ]
)
class EmailAuthenticationBackendTestCase(TestCase):

    def create_user(self, username, email, password):
        user = User.objects.create_user(username, email=email, password=password)
        return user

    def test_successful_auth(self):
        created_user = self.create_user("user1", "user1@example.com", "password")
        authed_user = authenticate(username="user1@example.com", password="password")
        self.assertTrue(authed_user is not None)
        self.assertEqual(created_user.pk, authed_user.pk)

    def test_unsuccessful_auth(self):
        authed_user = authenticate(username="user-does-not-exist", password="password")
        self.assertTrue(authed_user is None)

    def test_missing_credentials(self):
        self.create_user("user1", "user1@example.com", "password")
        self.assertTrue(authenticate() is None)
        self.assertTrue(authenticate(username="user1@example.com") is None)

    def test_successful_auth_django_2_1(self):
        created_user = self.create_user("user1", "user1@example.com", "password")
        request = None
        authed_user = authenticate(request, username="user1@example.com", password="password")
        self.assertTrue(authed_user is not None)
        self.assertEqual(created_user.pk, authed_user.pk)

    def test_unsuccessful_auth_django_2_1(self):
        request = None
        authed_user = authenticate(request, username="user-does-not-exist", password="password")
        self.assertTrue(authed_user is None)
