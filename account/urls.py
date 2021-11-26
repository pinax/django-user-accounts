from django.urls import path

from account.views import (
    ChangePasswordView,
    ConfirmEmailView,
    DeleteView,
    LoginView,
    LogoutView,
    PasswordResetTokenView,
    PasswordResetView,
    SettingsView,
    SignupView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="account_signup"),
    path("login/", LoginView.as_view(), name="account_login"),
    path("logout/", LogoutView.as_view(), name="account_logout"),
    path("confirm_email/<str:key>/", ConfirmEmailView.as_view(), name="account_confirm_email"),
    path("password/", ChangePasswordView.as_view(), name="account_password"),
    path("password/reset/", PasswordResetView.as_view(), name="account_password_reset"),
    path("password/reset/<str:uidb36>/<str:token>/", PasswordResetTokenView.as_view(), name="account_password_reset_token"),
    path("settings/", SettingsView.as_view(), name="account_settings"),
    path("delete/", DeleteView.as_view(), name="account_delete"),
]
