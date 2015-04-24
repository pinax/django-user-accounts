from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User

from account.models import SignupCode


class SignupViewTestCase(TestCase):

    def test_get(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
        }
        response = self.client.post(reverse("account_signup"), data)
        self.assertEqual(response.status_code, 302)

    def test_closed(self):
        with self.settings(ACCOUNT_OPEN_SIGNUP=False):
            data = {
                "username": "foo",
                "password": "bar",
                "password_confirm": "bar",
                "email": "foobar@example.com",
            }
            response = self.client.post(reverse("account_signup"), data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.template_name, "account/signup_closed.html")

    def test_valid_code(self):
        signup_code = SignupCode.create()
        signup_code.save()
        with self.settings(ACCOUNT_OPEN_SIGNUP=False):
            data = {
                "username": "foo",
                "password": "bar",
                "password_confirm": "bar",
                "email": "foobar@example.com",
                "code": signup_code.code,
            }
            response = self.client.post(reverse("account_signup"), data)
            self.assertEqual(response.status_code, 302)

    def test_invalid_code(self):
        with self.settings(ACCOUNT_OPEN_SIGNUP=False):
            data = {
                "username": "foo",
                "password": "bar",
                "password_confirm": "bar",
                "email": "foobar@example.com",
                "code": "abc123",
            }
            response = self.client.post(reverse("account_signup"), data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.template_name, "account/signup_closed.html")

    def test_get_authenticated(self):
        User.objects.create_user("foo", password="bar")
        self.client.login(username="foo", password="bar")

        with self.settings(ACCOUNT_LOGIN_REDIRECT_URL="/logged-in/"):
            response = self.client.get(reverse("account_signup"))
            self.assertRedirects(response, "/logged-in/", fetch_redirect_response=False)

    def test_post_authenticated(self):
        User.objects.create_user("foo", password="bar")
        self.client.login(username="foo", password="bar")

        with self.settings(ACCOUNT_LOGIN_REDIRECT_URL="/logged-in/"):
            data = {
                "username": "foo",
                "password": "bar",
                "password_confirm": "bar",
                "email": "foobar@example.com",
                "code": "abc123",
            }
            response = self.client.post(reverse("account_signup"), data)
            self.assertEqual(response.status_code, 404)


class LoginViewTestCase(TestCase):

    def test_get(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/login.html"])
