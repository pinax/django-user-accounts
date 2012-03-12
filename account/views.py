from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.contrib import auth, messages
from django.contrib.auth.models import User

from account import signals
from account.conf import settings
from account.forms import SignupForm, LoginUsernameForm
from account.models import EmailAddress
from account.utils import default_redirect, user_display


class SignupView(FormView):
    
    template_name = "account/signup.html"
    template_name_verification_sent = "account/verification_sent.html"
    form_class = SignupForm
    messages = {
        "email_verification_sent": {
            "level": messages.INFO,
            "text": _("Confirmation email sent to %(email)s")
        },
        "logged_in": {
            "level": messages.SUCCESS,
            "text": _("Successfully logged in as %(user)s")
        }
    }
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL))
        return super(SignupView, self).get(*args, **kwargs)
    
    def form_invalid(self, form):
        signals.user_sign_up_attempt.send(
            sender=SignupForm,
            username=form.data.get("username"),
            email=form.data.get("email"),
            result=form.is_valid()
        )
        return super(SignupView, self).form_invalid(form)
    
    def form_valid(self, form):
        new_user = self.create_user(form, commit=False)
        if settings.ACCOUNT_EMAIL_VERIFICATION:
            new_user.is_active = False
        new_user.save()
        EmailAddress.objects.add_email(new_user, form.cleaned_data["email"])
        self.after_signup(new_user)
        if settings.ACCOUNT_EMAIL_REQUIRE_CONFIRMATION:
            if self.messages.get("email_confirmation_sent"):
                messages.add_message(
                    self.request,
                    self.messages["email_confirmation_sent"]["level"],
                    self.messages["email_confirmation_sent"]["text"] % {
                        "email": form.cleaned_data["email"]
                    }
                )
            response_kwargs = {
                "request": self.request,
                "template": self.template_name_verification_sent,
                "context": {
                    "email": form.cleaned_data["email"],
                    "success_url": self.get_success_url(),
                }
            }
            return self.response_class(**response_kwargs)
        else:
            self.login_user(new_user)
            if self.messages.get("logged_in"):
                messages.add_message(
                    self.request,
                    self.messages["logged_in"]["level"],
                    self.messages["logged_in"]["text"] % {
                        "user": user_display(new_user)
                    }
                )
        return super(SignupView, self).form_valid(form)
    
    def get_success_url(self):
        return default_redirect(self.request, settings.ACCOUNT_SIGNUP_REDIRECT_URL)
    
    def create_user(self, form, commit=True):
        user = User()
        username = form.cleaned_data.get("username")
        if username is None:
            username = self.generate_username(form)
        user.username = username
        user.email = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user
    
    def generate_username(self, form):
        raise NotImplementedError("Unable to generate username by default. "
            "Override SignupView.generate_username in a subclass.")
    
    def after_signup(self, user):
        signals.user_signed_up.send(sender=SignupForm, user=user)
    
    def login_user(self, user):
        # set backend on User object to bypass needing to call auth.authenticate
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth.login(self.request, user)
        self.request.session.set_expiry(0)


class LoginView(FormView):
    
    template_name = "account/login.html"
    form_class = LoginUsernameForm
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(self.get_success_url())
        return super(LoginView, self).get(*args, **kwargs)
    
    def form_valid(self, form):
        self.login_user(form)
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL)
    
    def login_user(self, form):
        auth.login(self.request, form.user)
        self.request.session.set_expiry(
            60*60*24*365*10 if form.cleaned_data.get("remember") else 0
        )


class LogoutView(TemplateView):
    
    template_name = "account/logout.html"
    
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        return self.render_to_response({})
    
    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        return redirect(self.get_redirect_url())
    
    def get_redirect_url(self):
        return default_redirect(self.request, settings.ACCOUNT_LOGOUT_REDIRECT_URL)
