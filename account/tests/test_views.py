from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.utils import unittest

from django.contrib.auth.models import AnonymousUser

from account.views import SignupView, LoginView


class SignupDisabledView(SignupView):
    
    def disabled(self):
        return True


class LoginDisabledView(LoginView):
    
    def disabled(self):
        return True


class SignupViewTestCase(unittest.TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get(self):
        request = self.factory.get(reverse("account_signup"))
        response = SignupView.as_view()(request)
        self.assertEqual(response.status_code, 200)
    
    def test_get_disabled(self):
        request = self.factory.get(reverse("account_signup"))
        response = SignupDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 404)
    
    def test_post_disabled(self):
        request = self.factory.post(reverse("account_signup"))
        response = SignupDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 404)


class LoginViewTestCase(unittest.TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get(self):
        request = self.factory.get(reverse("account_login"))
        request.user = AnonymousUser()
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
    
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
