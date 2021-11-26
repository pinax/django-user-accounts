import django.dispatch

user_signed_up = django.dispatch.Signal()
user_sign_up_attempt = django.dispatch.Signal()
user_logged_in = django.dispatch.Signal()
user_login_attempt = django.dispatch.Signal()
signup_code_sent = django.dispatch.Signal()
signup_code_used = django.dispatch.Signal()
email_confirmed = django.dispatch.Signal()
email_confirmation_sent = django.dispatch.Signal()
password_changed = django.dispatch.Signal()
password_expired = django.dispatch.Signal()
