from django.test import TestCase

from account.models import SignupCode


class SignupCodeModelTestCase(TestCase):
    def test_exists_no_match(self):
        code = SignupCode(email="foobar@example.com", code="FOOFOO")
        code.save()

        self.assertFalse(SignupCode.exists(code="BARBAR"))
        self.assertFalse(SignupCode.exists(email="bar@example.com"))
        self.assertFalse(SignupCode.exists(email="bar@example.com", code="BARBAR"))
        self.assertFalse(SignupCode.exists())

    def test_exists_email_only_match(self):
        code = SignupCode(email="foobar@example.com", code="FOOFOO")
        code.save()

        self.assertTrue(SignupCode.exists(email="foobar@example.com"))

    def test_exists_code_only_match(self):
        code = SignupCode(email="foobar@example.com", code="FOOFOO")
        code.save()

        self.assertTrue(SignupCode.exists(code="FOOFOO"))
        self.assertTrue(SignupCode.exists(email="bar@example.com", code="FOOFOO"))

    def test_exists_email_match_code_mismatch(self):
        code = SignupCode(email="foobar@example.com", code="FOOFOO")
        code.save()

        self.assertTrue(SignupCode.exists(email="foobar@example.com", code="BARBAR"))

    def test_exists_code_match_email_mismatch(self):
        code = SignupCode(email="foobar@example.com", code="FOOFOO")
        code.save()

        self.assertTrue(SignupCode.exists(email="bar@example.com", code="FOOFOO"))

    def test_exists_both_match(self):
        code = SignupCode(email="foobar@example.com", code="FOOFOO")
        code.save()

        self.assertTrue(SignupCode.exists(email="foobar@example.com", code="FOOFOO"))
