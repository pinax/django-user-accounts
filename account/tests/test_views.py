from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.http import int_to_base36
from django.utils.six.moves.urllib.parse import urlparse

from django.contrib.auth.models import User

from account.compat import reverse
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

    def signup(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "code": "abc123",
        }
        self.client.post(reverse("account_signup"), data)
        self.client.logout()

    def test_get(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/login.html"])

    def test_post_empty(self):
        data = {}
        response = self.client.post(reverse("account_login"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            "account.auth_backends.UsernameAuthenticationBackend",
        ]
    )
    def test_post_success(self):
        self.signup()
        data = {
            "username": "foo",
            "password": "bar",
        }
        response = self.client.post(reverse("account_login"), data)
        self.assertRedirects(
            response,
            settings.ACCOUNT_LOGIN_REDIRECT_URL,
            fetch_redirect_response=False
        )


class LogoutViewTestCase(TestCase):

    def signup(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "code": "abc123",
        }
        self.client.post(reverse("account_signup"), data)

    def test_get_anonymous(self):
        response = self.client.get(reverse("account_logout"))
        self.assertRedirects(
            response,
            settings.ACCOUNT_LOGOUT_REDIRECT_URL,
            fetch_redirect_response=False
        )

    def test_get_authenticated(self):
        self.signup()
        response = self.client.get(reverse("account_logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/logout.html"])

    def test_post_anonymous(self):
        response = self.client.post(reverse("account_logout"), {})
        self.assertRedirects(
            response,
            settings.ACCOUNT_LOGOUT_REDIRECT_URL,
            fetch_redirect_response=False
        )

    def test_post_authenticated(self):
        self.signup()
        response = self.client.post(reverse("account_logout"), {})
        self.assertRedirects(
            response,
            settings.ACCOUNT_LOGOUT_REDIRECT_URL,
            fetch_redirect_response=False
        )


class ConfirmEmailViewTestCase(TestCase):

    def signup(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "code": "abc123",
        }
        self.client.post(reverse("account_signup"), data)
        return EmailConfirmation.objects.get()

    def test_get_good_key(self):
        email_confirmation = self.signup()
        response = self.client.get(reverse("account_confirm_email", kwargs={"key": email_confirmation.key}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/email_confirm.html"])

    def test_get_bad_key(self):
        response = self.client.get(reverse("account_confirm_email", kwargs={"key": "badkey"}))
        self.assertEqual(response.status_code, 404)

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_REQUIRED=True)
    def test_post_required(self):
        email_confirmation = self.signup()
        response = self.client.post(reverse("account_confirm_email", kwargs={"key": email_confirmation.key}), {})
        self.assertRedirects(
            response,
            reverse(settings.ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL),
            fetch_redirect_response=False
        )

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_REQUIRED=False)
    def test_post_not_required(self):
        email_confirmation = self.signup()
        response = self.client.post(reverse("account_confirm_email", kwargs={"key": email_confirmation.key}), {})
        self.assertRedirects(
            response,
            settings.ACCOUNT_LOGIN_REDIRECT_URL,
            fetch_redirect_response=False
        )

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_REQUIRED=False, ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL="/somewhere/")
    def test_post_not_required_redirect_override(self):
        email_confirmation = self.signup()
        response = self.client.post(reverse("account_confirm_email", kwargs={"key": email_confirmation.key}), {})
        self.assertRedirects(
            response,
            settings.ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL,
            fetch_redirect_response=False
        )

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_REQUIRED=True,
        ACCOUNT_EMAIL_CONFIRMATION_AUTO_LOGIN=True,
        ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL="/somewhere/",
    )
    def test_post_auto_login(self):
        email_confirmation = self.signup()
        response = self.client.post(reverse("account_confirm_email", kwargs={"key": email_confirmation.key}), {})
        self.assertRedirects(
            response,
            settings.ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL,
            fetch_redirect_response=False
        )


class ChangePasswordViewTestCase(TestCase):

    def signup(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "code": "abc123",
        }
        self.client.post(reverse("account_signup"), data)
        mail.outbox = []
        return User.objects.get(username="foo")

    def test_get_anonymous(self):
        response = self.client.get(reverse("account_password"))
        self.assertRedirects(
            response,
            reverse("account_password_reset"),
            fetch_redirect_response=False
        )

    def test_get_authenticated(self):
        self.signup()
        response = self.client.get(reverse("account_password"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/password_change.html"])

    def test_post_anonymous(self):
        data = {
            "password_current": "password",
            "password_new": "new-password",
            "password_new_confirm": "new-password",
        }
        response = self.client.post(reverse("account_password"), data)
        self.assertEqual(response.status_code, 403)

    def test_post_authenticated_success(self):
        user = self.signup()
        data = {
            "password_current": "bar",
            "password_new": "new-bar",
            "password_new_confirm": "new-bar",
        }
        response = self.client.post(reverse("account_password"), data)
        self.assertRedirects(
            response,
            reverse(settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL),
            fetch_redirect_response=False
        )
        updated_user = User.objects.get(username=user.username)
        self.assertNotEqual(user.password, updated_user.password)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE=False)
    def test_post_authenticated_success_no_mail(self):
        self.signup()
        data = {
            "password_current": "bar",
            "password_new": "new-bar",
            "password_new_confirm": "new-bar",
        }
        response = self.client.post(reverse("account_password"), data)
        self.assertRedirects(
            response,
            reverse(settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL),
            fetch_redirect_response=False
        )
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetTokenViewTestCase(TestCase):

    def signup(self):
        data = {
            "username": "foo",
            "password": "bar",
            "password_confirm": "bar",
            "email": "foobar@example.com",
            "code": "abc123",
        }
        self.client.post(reverse("account_signup"), data)
        mail.outbox = []
        return User.objects.get(username="foo")

    def request_password_reset(self):
        user = self.signup()
        data = {
            "email": user.email,
        }
        self.client.post(reverse("account_password_reset"), data)
        parsed = urlparse(mail.outbox[0].body.strip())
        return user, parsed.path

    def test_get_bad_user(self):
        url = reverse(
            "account_password_reset_token",
            kwargs={
                "uidb36": int_to_base36(100),
                "token": "notoken",
            }
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_reset(self):
        user, url = self.request_password_reset()
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(
                "account_password_reset_token",
                kwargs={
                    "uidb36": int_to_base36(user.id),
                    "token": "set-password",
                }
            ),
            fetch_redirect_response=False
        )

    def test_post_reset(self):
        user, url = self.request_password_reset()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        data = {
            "password": "new-password",
            "password_confirm": "new-password",
        }
        response = self.client.post(response["Location"], data)
        self.assertRedirects(
            response,
            reverse(settings.ACCOUNT_PASSWORD_RESET_REDIRECT_URL),
            fetch_redirect_response=False
        )
