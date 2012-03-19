from django.conf.urls import patterns, url

from django.contrib.auth.decorators import login_required

from account.views import SignupView, LoginView, LogoutView, ChangePasswordView, PasswordResetView, PasswordResetDoneView, PasswordResetKeyView
from account.views import ConfirmEmailView


urlpatterns = patterns("",
    url(r"^signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^login/$", LoginView.as_view(), name="account_login"),
    url(r"^logout/$", LogoutView.as_view(), name="account_logout"),
    url(r"^confirm_email/(?P<key>\w+)/$", ConfirmEmailView.as_view(), name="account_confirm_email"),
    url(r"^password_change/$", login_required(ChangePasswordView.as_view()), name="account_password"),
    url(r"^password_reset/$", PasswordResetView.as_view(), name="account_password_reset"),
    url(r"^password_reset_done/$", PasswordResetDoneView.as_view(), name="account_password_reset_done"),
    url(r"^password_reset_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", PasswordResetKeyView.as_view(), name="account_password_reset_key"),
)
