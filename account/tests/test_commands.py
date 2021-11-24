from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from ..conf import settings
from ..models import PasswordExpiry, PasswordHistory


@override_settings(
    ACCOUNT_PASSWORD_EXPIRY=500
)
class UserPasswordExpiryTests(TestCase):

    def setUp(self):
        self.UserModel = get_user_model()
        self.user = self.UserModel.objects.create_user(username="patrick")

    def test_set_explicit_password_expiry(self):
        """
        Ensure specific password expiry is set.
        """
        self.assertFalse(hasattr(self.user, "password_expiry"))
        expiration_period = 60
        out = StringIO()
        call_command(
            "user_password_expiry",
            "patrick",
            "--expire={}".format(expiration_period),
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        user_expiry = user.password_expiry
        self.assertEqual(user_expiry.expiry, expiration_period)
        self.assertIn('User "{}" password expiration set to {} seconds'.format(self.user.username, expiration_period), out.getvalue())

    def test_set_default_password_expiry(self):
        """
        Ensure default password expiry (from settings) is set.
        """
        self.assertFalse(hasattr(self.user, "password_expiry"))
        out = StringIO()
        call_command(
            "user_password_expiry",
            "patrick",
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        user_expiry = user.password_expiry
        default_expiration = settings.ACCOUNT_PASSWORD_EXPIRY
        self.assertEqual(user_expiry.expiry, default_expiration)
        self.assertIn('User "{}" password expiration set to {} seconds'.format(self.user.username, default_expiration), out.getvalue())

    def test_reset_existing_password_expiry(self):
        """
        Ensure existing password expiry is reset.
        """
        previous_expiry = 123
        existing_expiry = PasswordExpiry.objects.create(user=self.user, expiry=previous_expiry)
        out = StringIO()
        call_command(
            "user_password_expiry",
            "patrick",
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        user_expiry = user.password_expiry
        self.assertEqual(user_expiry, existing_expiry)
        default_expiration = settings.ACCOUNT_PASSWORD_EXPIRY
        self.assertEqual(user_expiry.expiry, default_expiration)
        self.assertNotEqual(user_expiry.expiry, previous_expiry)

    def test_bad_username(self):
        """
        Ensure proper operation when username is not found.
        """
        bad_username = "asldkfj"
        out = StringIO()
        call_command(
            "user_password_expiry",
            bad_username,
            stdout=out
        )
        self.assertIn('User "{}" not found'.format(bad_username), out.getvalue())


class UserPasswordHistoryTests(TestCase):

    def setUp(self):
        self.UserModel = get_user_model()
        self.user = self.UserModel.objects.create_user(username="patrick")

    def test_set_history(self):
        """
        Ensure password history is created.
        """
        self.assertFalse(self.user.password_history.all())
        password_age = 5  # days
        out = StringIO()
        call_command(
            "user_password_history",
            "--days={}".format(password_age),
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)
        self.assertIn("Password history set to ", out.getvalue())
        self.assertIn("for {} users".format(1), out.getvalue())

    def test_set_history_exists(self):
        """
        Ensure password history is NOT created.
        """
        PasswordHistory.objects.create(user=self.user)
        password_age = 5  # days
        out = StringIO()
        call_command(
            "user_password_history",
            "--days={}".format(password_age),
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)
        self.assertIn("No users found without password history", out.getvalue())

    def test_set_history_one_exists(self):
        """
        Ensure password history is created for users without existing history.
        """
        another_user = self.UserModel.objects.create_user(username="james")
        PasswordHistory.objects.create(user=another_user)

        password_age = 5  # days
        out = StringIO()
        call_command(
            "user_password_history",
            "--days={}".format(password_age),
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)

        # verify user with existing history did not get another entry
        user = self.UserModel.objects.get(username="james")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)

        self.assertIn("Password history set to ", out.getvalue())
        self.assertIn("for {} users".format(1), out.getvalue())

    def test_set_history_force(self):
        """
        Ensure specific password history is created for all users.
        """
        another_user = self.UserModel.objects.create_user(username="james")
        PasswordHistory.objects.create(user=another_user)

        password_age = 5  # days
        out = StringIO()
        call_command(
            "user_password_history",
            "--days={}".format(password_age),
            "--force",
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)

        # verify user with existing history DID get another entry
        user = self.UserModel.objects.get(username="james")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 2)

        self.assertIn("Password history set to ", out.getvalue())
        self.assertIn("for {} users".format(2), out.getvalue())

    def test_set_history_multiple(self):
        """
        Ensure password history is created for all users without existing history.
        """
        self.UserModel.objects.create_user(username="second")
        self.UserModel.objects.create_user(username="third")

        password_age = 5  # days
        out = StringIO()
        call_command(
            "user_password_history",
            "--days={}".format(password_age),
            stdout=out
        )

        user = self.UserModel.objects.get(username="patrick")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)
        first_timestamp = password_history[0].timestamp

        user = self.UserModel.objects.get(username="second")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)
        second_timestamp = password_history[0].timestamp
        self.assertEqual(first_timestamp, second_timestamp)

        user = self.UserModel.objects.get(username="third")
        password_history = user.password_history.all()
        self.assertEqual(password_history.count(), 1)
        third_timestamp = password_history[0].timestamp
        self.assertEqual(first_timestamp, third_timestamp)

        self.assertIn("Password history set to ", out.getvalue())
        self.assertIn("for {} users".format(3), out.getvalue())
