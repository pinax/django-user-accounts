from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.utils import unittest

from django.contrib.auth.models import AnonymousUser, User

from account.views import SignupView, LoginView


class SignupEnabledView(SignupView):
    
    def is_open(self):
        return True


class SignupDisabledView(SignupView):
    
    def is_open(self):
        return False


class LoginDisabledView(LoginView):
    
    def disabled(self):
        return True


class SignupViewTestCase(unittest.TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get(self):
        request = self.factory.get(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupEnabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
    
    def test_get_disabled(self):
        request = self.factory.get(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "account/signup_closed.html")
    
    def test_post_disabled(self):
        request = self.factory.post(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "account/signup_closed.html")
    
    def test_post_successful(self):
        post = {"username": "user", "password": "pwd",
            "password_confirm": "pwd", "email": "info@example.com"}
        request = self.factory.post(reverse("account_signup"), post)
        request.user = AnonymousUser()
        response = SignupEnabledView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="user")
        self.asserEqual(user.email, "info@example.com")


class LoginViewTestCase(unittest.TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get(self):
        request = self.factory.get(reverse("account_login"))
        request.user = AnonymousUser()
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/login.html"])

    def test_get_disabled(self):
        request = self.factory.get(reverse("account_login"))
        request.user = AnonymousUser()
        response = LoginDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
    
    def test_post_disabled(self):
        request = self.factory.post(reverse("account_login"))
        request.user = AnonymousUser()
        response = LoginDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 403)
