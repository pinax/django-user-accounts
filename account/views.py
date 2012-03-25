from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import FormView

from django.contrib import auth, messages
from django.contrib.auth.models import User

from account import signals
from account.conf import settings
from account.forms import SignupForm, LoginUsernameForm
from account.models import SignupCode, EmailAddress, EmailConfirmation
from account.utils import default_redirect, user_display


class SignupView(FormView):
    
    template_name = "account/signup.html"
    template_name_email_confirmation_sent = "account/email_confirmation_sent.html"
    template_name_signup_closed = "account/signup_closed.html"
    form_class = SignupForm
    redirect_field_name = "next"
    messages = {
        "email_confirmation_sent": {
            "level": messages.INFO,
            "text": _("Confirmation email sent to %(email)s")
        },
        "logged_in": {
            "level": messages.SUCCESS,
            "text": _("Successfully logged in as %(user)s")
        },
        "invalid_signup_code": {
            "level": messages.WARNING,
            "text": _("The code %(code)s is invalid")
        }
    }
    
    def __init__(self, *args, **kwargs):
        kwargs["signup_code"] = None
        super(SignupView, self).__init__(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL))
        code = self.request.GET.get("code")
        try:
            self.signup_code = SignupCode.check(code)
        except SignupCode.InvalidCode:
            if not settings.ACCOUNT_OPEN_SIGNUP:
                return self.closed(code=code)
            else:
                if self.messages.get("invalid_signup_code"):
                    messages.add_message(
                        self.request,
                        self.messages["invalid_signup_code"]["level"],
                        self.messages["invalid_signup_code"]["text"] % {
                            "code": code
                        }
                    )
        if not settings.ACCOUNT_OPEN_SIGNUP and self.signup_code is None:
            return self.closed()
        return super(SignupView, self).get(*args, **kwargs)
    
    def get_initial(self):
        initial = super(SignupView, self).get_initial()
        if self.signup_code:
            initial["code"] = self.signup_code.code
        return initial
    
    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            "redirect_field_name": redirect_field_name,
            "redirect_field_value": self.request.REQUEST.get(redirect_field_name),
        })
        return ctx
    
    def form_invalid(self, form):
        signals.user_sign_up_attempt.send(
            sender=SignupForm,
            username=form.data.get("username"),
            email=form.data.get("email"),
            result=form.is_valid()
        )
        return super(SignupView, self).form_invalid(form)
    
    def form_valid(self, form):
        email_confirmed = False
        new_user = self.create_user(form, commit=False)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
            new_user.is_active = False
        new_user.save()
        signup_code = form.cleaned_data.get("code")
        if signup_code:
            signup_code.use(new_user)
            if signup_code.email and form.cleaned_data["email"] == signup_code.email:
                EmailAddress.objects.create(
                    user=new_user,
                    email=form.cleaned_data["email"],
                    primary=True,
                    verified=True
                )
                email_confirmed = True
            else:
                EmailAddress.objects.add_email(new_user, form.cleaned_data["email"])
        else:
            EmailAddress.objects.add_email(new_user, form.cleaned_data["email"])
        self.after_signup(new_user, form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_confirmed:
            response_kwargs = {
                "request": self.request,
                "template": self.template_name_email_confirmation_sent,
                "context": {
                    "email": form.cleaned_data["email"],
                    "success_url": self.get_success_url(),
                }
            }
            return self.response_class(**response_kwargs)
        else:
            if self.messages.get("email_confirmation_sent") and not email_confirmed:
                messages.add_message(
                    self.request,
                    self.messages["email_confirmation_sent"]["level"],
                    self.messages["email_confirmation_sent"]["text"] % {
                        "email": form.cleaned_data["email"]
                    }
                )
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
    
    def get_redirect_field_name(self):
        return self.redirect_field_name
    
    def create_user(self, form, commit=True, **kwargs):
        user = User(**kwargs)
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
    
    def after_signup(self, user, form):
        signals.user_signed_up.send(sender=SignupForm, user=user)
    
    def login_user(self, user):
        # set backend on User object to bypass needing to call auth.authenticate
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth.login(self.request, user)
        self.request.session.set_expiry(0)
    
    def closed(self, code=None):
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_signup_closed,
            "context": {
                "code": code,
            }
        }
        return self.response_class(**response_kwargs)


class LoginView(FormView):
    
    template_name = "account/login.html"
    form_class = LoginUsernameForm
    redirect_field_name = "next"
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(self.get_success_url())
        return super(LoginView, self).get(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            "redirect_field_name": redirect_field_name,
            "redirect_field_value": self.request.REQUEST.get(redirect_field_name),
        })
        return ctx
    
    def form_valid(self, form):
        self.login_user(form)
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL)
    
    def get_redirect_field_name(self):
        return self.redirect_field_name
    
    def login_user(self, form):
        auth.login(self.request, form.user)
        self.request.session.set_expiry(
            60*60*24*365*10 if form.cleaned_data.get("remember") else 0
        )


class LogoutView(TemplateResponseMixin, View):
    
    template_name = "account/logout.html"
    
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        ctx = self.get_context_data()
        return self.render_to_response(ctx)
    
    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        return redirect(self.get_redirect_url())
    
    def get_context_data(self):
        return {}
    
    def get_redirect_url(self):
        return default_redirect(self.request, settings.ACCOUNT_LOGOUT_REDIRECT_URL)


class ConfirmEmailView(TemplateResponseMixin, View):
    
    messages = {
        "email_confirmed": {
            "level": messages.SUCCESS,
            "text": _("You have confirmed %(email)s")
        }
    }
    
    def get_template_names(self):
        return {
            "GET": ["account/email_confirm.html"],
            "POST": ["account/email_confirmed.html"],
        }[self.request.method]
    
    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        if confirmation.email_address.user != self.request.user:
            raise Http404()
        ctx = self.get_context_data()
        return self.render_to_response(ctx)
    
    def post(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        if confirmation.email_address.user != self.request.user:
            raise Http404()
        confirmation.confirm()
        user = confirmation.email_address.user
        user.is_active = True
        user.save()
        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)
        if self.messages.get("email_confirmed"):
            messages.add_message(
                self.request,
                self.messages["email_confirmed"]["level"],
                self.messages["email_confirmed"]["text"] % {
                    "email": confirmation.email_address.email
                }
            )
        return redirect(redirect_url)
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.get(key=self.kwargs["key"].lower())
        except EmailConfirmation.DoesNotExist:
            raise Http404()
    
    def get_queryset(self):
        qs = EmailConfirmation.objects.all()
        qs = qs.select_related("email_address__user")
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        return ctx
    
    def get_redirect_url(self):
        if self.request.user.is_authenticated():
            if not settings.ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL:
                return settings.ACCOUNT_LOGIN_REDIRECT_URL
            return settings.ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL
        else:
            return settings.ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL
