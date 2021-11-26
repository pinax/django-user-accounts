import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

import pytz
from account.models import PasswordHistory


class Command(BaseCommand):

    help = "Create password history for all users without existing history."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--days",
            type=int,
            nargs="?",
            default=10,
            help="age of current password (in days)"
        )
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="create new password history for all users, regardless of existing history"
        )

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all()
        if not options["force"]:
            users = users.filter(password_history=None)

        if not users:
            return "No users found without password history"

        days = options["days"]
        timestamp = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(days=days)

        # Create new PasswordHistory on `timestamp`
        PasswordHistory.objects.bulk_create(
            [PasswordHistory(user=user, timestamp=timestamp) for user in users]
        )

        return "Password history set to {} for {} users".format(timestamp, len(users))
