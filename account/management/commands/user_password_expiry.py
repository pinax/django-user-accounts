from django.core.management.base import LabelCommand

from account.conf import settings
from account.models import PasswordExpiry


class Command(LabelCommand):

    help = "Create user-specific password expiration."
    label = "username"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("-e", "--expire", default=settings.ACCOUNT_PASSWORD_EXPIRY)

    def handle_label(self, username, **options):
        try:
            user = settings.AUTH_USER_MODEL.objects.get(username=username)
        except settings.AUTH_USER_MODEL.DoesNotExist:
            return "User \"{}\" not found".format(username)

        expire = options["expire"]

        # Modify existing PasswordExpiry or create new if needed.
        if not hasattr(user, "password_expiry"):
            PasswordExpiry.objects.create(user=user, expiry=expire)
        else:
            user.password_expiry.expiry = expire
            user.password_expiry.save()

        return "User \"{}\" password expiration now {} seconds".format(username, expire)
