.. _commands:

===================
Management Commands
===================

user_password_history
---------------------

Creates an initial password history for all users who don't already
have a password history.

Accepts two optional arguments::

    -d --days <days> - Sets the age of the current password. Default is 10 days.
    -f --force - Sets a new password history for ALL users, regardless of prior history.

user_password_expiry
--------------------

Creates a password expiry specific to one user.

Password expiration checks use a global value (``ACCOUNT_PASSWORD_EXPIRY``)
for the expiration time period. This value can be superseded on a per-user basis
by creating a user password expiry.

Requires one argument::

    <username> [<username>] - username(s) of the user(s) who needs specific password expiry.

Accepts one optional argument::

    -e --expire <seconds> - Sets the number of seconds for password expiration.
                            Default is the current global ACCOUNT_PASSWORD_EXPIRY value.

After creation, you can modify user password expiration from the Django
admin. Find the desired user at ``/admin/account/passwordexpiry/`` and change the ``expiry`` value.
