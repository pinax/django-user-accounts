from django.contrib.auth.models import User
from django.forms import ValidationError
from django.test import TestCase, override_settings

from account.models import EmailAddress


@override_settings(ACCOUNT_EMAIL_UNIQUE=True)
class UniqueEmailAddressTestCase(TestCase):
    def test_unique_email(self):
        user = User.objects.create_user("user1", email="user1@example.com", password="password")

        email_1 = EmailAddress(user=user, email="user2@example.com")
        email_1.full_clean()
        email_1.save()

        validation_error = False
        try:
            email_2 = EmailAddress(user=user, email="USER2@example.com")
            email_2.full_clean()
            email_2.save()
        except ValidationError:
            validation_error = True

        self.assertTrue(validation_error)
