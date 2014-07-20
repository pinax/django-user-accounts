from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from django.contrib.auth.models import AnonymousUser

from account.views import SignupView, LoginView


class SignupEnabledView(SignupView):

    def is_open(self):
        return True


class SignupViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        request = self.factory.get(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupEnabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class LoginViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        request = self.factory.get(reverse("account_login"))
        request.user = AnonymousUser()
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/login.html"])
