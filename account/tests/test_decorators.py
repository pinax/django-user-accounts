from unittest import mock

from django.http import HttpResponse
from django.test import TestCase

from account.decorators import login_required


@login_required
def mock_view(request, *args, **kwargs):
    return HttpResponse("OK", status=200)


class LoginRequiredDecoratorTestCase(TestCase):

    def test_authenticated_user_is_allowed(self):
        request = mock.MagicMock()
        request.user.is_authenticated = True
        response = mock_view(request)
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_gets_redirected(self):
        request = mock.MagicMock()
        request.user.is_authenticated = False
        response = mock_view(request)
        self.assertEqual(response.status_code, 302)
