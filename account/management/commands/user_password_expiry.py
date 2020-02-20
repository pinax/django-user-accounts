from django.contrib.auth import get_user_model
from django.core.management.base import LabelCommand

from account.conf import settings
from account.models import PasswordExpiry


class Command(LabelCommand):

    help = "Create user-specific password expiration period."
    label = "username"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "-e", "--expire",
            type=int,
            nargs="?",
            default=settings.ACCOUNT_PASSWORD_EXPIRY,
            help="number of seconds until password expires"
        )

    def handle_label(self, username, **options):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return 'User "{}" not found'.format(username)

        expire = options["expire"]

        # Modify existing PasswordExpiry or create new if needed.
        if not hasattr(user, "password_expiry"):
            PasswordExpiry.objects.create(user=user, expiry=expire)
        else:
            user.password_expiry.expiry = expire
            user.password_expiry.save()

        return 'User "{}" password expiration set to {} seconds'.format(username, expire)
