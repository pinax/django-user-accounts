from django.test import TestCase
from account.hooks import AccountDefaultHookSet


class AccountDefaultHookSetTests(TestCase):

    def test_non_existing_template(self):
        """If template does not exist, then function must return None.
        """

        inst = AccountDefaultHookSet()
        ctx = {}
        actual = inst.render_to_string_or_none("account/email/template_not_exist.html", ctx)

        self.assertEquals(actual, None)

    def test_existing_template(self):
        """If template does exist, make sure it renders correctly.
        """

        inst = AccountDefaultHookSet()
        ctx = {}
        actual = inst.render_to_string_or_none("account/email/email_confirmation_message.html", ctx)
        expected = "<b>ccc</b>"
        self.assertEquals(actual, expected)
