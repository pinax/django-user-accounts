from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User

from account.models import SignupCode, EmailConfirmation


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

    def test_get_next_url(self):
        next_url = "/next-url/"
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
        }
        response = self.client.post("{}?next={}".format(reverse("account_signup"), next_url), data)
        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_post_next_url(self):
        next_url = "/next-url/"
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "next": next_url,
        }
        response = self.client.post(reverse("account_signup"), data)
        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_session_next_url(self):
        # session setup due to bug in Django 1.7
        setup_session(self.client)

        next_url = "/next-url/"
        session = self.client.session
        session["redirect_to"] = next_url
        session.save()
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
        }
        response = self.client.post(reverse("account_signup"), data)
        self.assertRedirects(response, next_url, fetch_redirect_response=False)


class LoginViewTestCase(TestCase):

    def test_get(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/login.html"])


class ConfirmEmailViewTestCase(TestCase):

    def test_get_good_key(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "code": "abc123",
        }
        self.client.post(reverse("account_signup"), data)
        email_confirmation = EmailConfirmation.objects.get()
        response = self.client.get(reverse("account_confirm_email", kwargs={"key": email_confirmation.key}))
        self.assertEqual(response.status_code, 200)

    def test_get_bad_key(self):
        response = self.client.get(reverse("account_confirm_email", kwargs={"key": "badkey"}))
        self.assertEqual(response.status_code, 404)


def setup_session(client):
    assert apps.is_installed("django.contrib.sessions"), "sessions not installed"
    engine = import_module(settings.SESSION_ENGINE)
    cookie = client.cookies.get(settings.SESSION_COOKIE_NAME, None)
    if cookie:
        return engine.SessionStore(cookie.value)
    s = engine.SessionStore()
    s.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
    return s
