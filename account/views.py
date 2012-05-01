from django.http import Http404, HttpResponseForbidden
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import base36_to_int, int_to_base36
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import FormView

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.contrib.auth.tokens import default_token_generator

from account import signals
from account.conf import settings
from account.forms import SignupForm, LoginUsernameForm
from account.forms import ChangePasswordForm, PasswordResetForm, PasswordResetTokenForm
from account.forms import SettingsForm
from account.mixins import LoginRequiredMixin
from account.models import SignupCode, EmailAddress, EmailConfirmation, Account
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
            "text": _("Confirmation email sent to %(email)s.")
        },
        "logged_in": {
            "level": messages.SUCCESS,
            "text": _("Successfully logged in as %(user)s.")
        },
        "invalid_signup_code": {
            "level": messages.WARNING,
            "text": _("The code %(code)s is invalid.")
        }
    }
    
    def __init__(self, *args, **kwargs):
        kwargs["signup_code"] = None
        super(SignupView, self).__init__(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(default_redirect(self.request, settings.ACCOUNT_LOGIN_REDIRECT_URL))
        if not self.is_open():
            return self.closed()
        return super(SignupView, self).get(*args, **kwargs)
    
    def post(self, *args, **kwargs):
        if not self.is_open():
            return self.closed()
        return super(SignupView, self).post(*args, **kwargs)
    
    def get_initial(self):
        initial = super(SignupView, self).get_initial()
        if self.signup_code:
            initial["code"] = self.signup_code.code
            if self.signup_code.email:
                initial["email"] = self.signup_code.email
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
        self.create_account(new_user, form)
        email_kwargs = {"primary": True}
        if self.signup_code:
            self.signup_code.use(new_user)
            if self.signup_code.email and new_user.email == self.signup_code.email:
                email_kwargs["verified"] = True
                email_confirmed = True
        EmailAddress.objects.add_email(new_user, new_user.email, **email_kwargs)
        self.after_signup(new_user, form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_confirmed:
            response_kwargs = {
                "request": self.request,
                "template": self.template_name_email_confirmation_sent,
                "context": {
                    "email": new_user.email,
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
        user.email = form.cleaned_data["email"].strip()
        password = form.cleaned_data.get("password")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user
    
    def create_account(self, new_user, form):
        return Account.create(request=self.request, user=new_user)
    
    def generate_username(self, form):
        raise NotImplementedError("Unable to generate username by default. "
            "Override SignupView.generate_username in a subclass.")
    
    def after_signup(self, user, form):
        signals.user_signed_up.send(sender=SignupForm, user=user, form=form)
    
    def login_user(self, user):
        # set backend on User object to bypass needing to call auth.authenticate
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth.login(self.request, user)
        self.request.session.set_expiry(0)
    
    def is_open(self):
        code = self.request.REQUEST.get("code")
        if code:
            try:
                self.signup_code = SignupCode.check(code)
            except SignupCode.InvalidCode:
                if not settings.ACCOUNT_OPEN_SIGNUP:
                    return False
                else:
                    if self.messages.get("invalid_signup_code"):
                        messages.add_message(
                            self.request,
                            self.messages["invalid_signup_code"]["level"],
                            self.messages["invalid_signup_code"]["text"] % {
                                "code": code
                            }
                        )
                    return True
            else:
                return True
        else:
            return settings.ACCOUNT_OPEN_SIGNUP
    
    def closed(self):
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_signup_closed,
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
        expiry = settings.ACCOUNT_REMEMBER_ME_EXPIRY if form.cleaned_data.get("remember") else 0
        self.request.session.set_expiry(expiry)


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
            "text": _("You have confirmed %(email)s.")
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


class ChangePasswordView(FormView):
    
    template_name = "account/password_change.html"
    form_class = ChangePasswordForm
    messages = {
        "password_changed": {
            "level": messages.SUCCESS,
            "text": _(u"Password successfully changed.")
        }
    }
    
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect("account_password_reset")
        return super(ChangePasswordView, self).get(*args, **kwargs)
    
    def post(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseForbidden()
        return super(ChangePasswordView, self).post(*args, **kwargs)
    
    def change_password(self, form):
        user = self.request.user
        form.save(user)
        if self.messages.get("password_changed"):
            messages.add_message(
                self.request,
                self.messages["password_changed"]["level"],
                self.messages["password_changed"]["text"]
            )
        signals.password_changed.send(sender=ChangePasswordForm, user=user)
    
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {"user": self.request.user, "initial": self.get_initial()}
        if self.request.method in ["POST", "PUT"]:
            kwargs.update({
                "data": self.request.POST,
                "files": self.request.FILES,
            })
        return kwargs
    
    def form_valid(self, form):
        self.change_password(form)
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return default_redirect(self.request, settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL)


class PasswordResetView(FormView):
    
    template_name = "account/password_reset.html"
    template_name_sent = "account/password_reset_sent.html"
    form_class = PasswordResetForm
    token_generator = default_token_generator
    
    def get_context_data(self, **kwargs):
        context = kwargs
        if self.request.method == "POST" and "resend" in self.request.POST:
            context["resend"] = True
        return context
    
    def form_valid(self, form):
        self.send_email(form.cleaned_data["email"])
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_sent,
            "context": self.get_context_data(form=form)
        }
        return self.response_class(**response_kwargs)
    
    def send_email(self, email):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = get_current_site(self.request)
        for user in User.objects.filter(email__iexact=email):
            uid = int_to_base36(user.id)
            token = self.make_token(user)
            password_reset_url = u"%s://%s%s" % (
                protocol,
                unicode(current_site.domain),
                reverse("account_password_reset_token", kwargs=dict(uidb36=uid, token=token))
            )
            ctx = {
                "user": user,
                "current_site": current_site,
                "password_reset_url": password_reset_url,
            }
            subject = render_to_string("account/email/password_reset_subject.txt", ctx)
            subject = "".join(subject.splitlines())
            message = render_to_string("account/email/password_reset.txt", ctx)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    
    def make_token(self, user):
        return self.token_generator.make_token(user)


class PasswordResetTokenView(FormView):
    
    template_name = "account/password_reset_token.html"
    template_name_fail = "account/password_reset_token_fail.html"
    form_class = PasswordResetTokenForm
    token_generator = default_token_generator
    messages = {
        "password_changed": {
            "level": messages.SUCCESS,
            "text": _("Password successfully changed.")
        },
    }
    
    def get(self, request, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ctx = self.get_context_data(form=form)
        if not self.check_token(self.get_user(), self.kwargs["token"]):
            return self.token_fail()
        return self.render_to_response(ctx)
    
    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "uidb36": self.kwargs["uidb36"],
            "token": self.kwargs["token"],
        })
        return ctx
    
    def form_valid(self, form):
        user = self.get_user()
        user.set_password(form.cleaned_data["password"])
        user.save()
        if self.messages.get("password_changed"):
            messages.add_message(
                self.request,
                self.messages["password_changed"]["level"],
                self.messages["password_changed"]["text"]
            )
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return settings.ACCOUNT_PASSWORD_RESET_REDIRECT_URL
    
    def get_user(self):
        try:
            uid_int = base36_to_int(self.kwargs["uidb36"])
        except ValueError:
            raise Http404()
        return get_object_or_404(User, id=uid_int)
    
    def check_token(self, user, token):
        return self.token_generator.check_token(user, token)
    
    def token_fail(self):
        response_kwargs = {
            "request": self.request,
            "template": self.template_name_fail,
            "context": self.get_context_data()
        }
        return self.response_class(**response_kwargs)


class SettingsView(LoginRequiredMixin, FormView):
    
    template_name = "account/settings.html"
    form_class = SettingsForm
    messages = {
        "settings_updated": {
            "level": messages.SUCCESS,
            "text": _("Account settings updated.")
        },
    }
    
    def get_form_class(self):
        # @@@ django: this is a workaround to not having a dedicated method
        # to initialize self with a request in a known good state (of course
        # this only works with a FormView)
        self.primary_email_address = EmailAddress.objects.get_primary(self.request.user)
        return super(SettingsView, self).get_form_class()
    
    def get_initial(self):
        initial = super(SettingsView, self).get_initial()
        if self.primary_email_address:
            initial["email"] = self.primary_email_address.email
        initial["timezone"] = self.request.user.account.timezone
        initial["language"] = self.request.user.account.language
        return initial
    
    def form_valid(self, form):
        self.update_settings(form)
        if self.messages.get("settings_updated"):
            messages.add_message(
                self.request,
                self.messages["settings_updated"]["level"],
                self.messages["settings_updated"]["text"]
            )
        return redirect(self.get_success_url())
    
    def update_settings(self, form):
        self.update_email(form)
        self.update_account(form)
    
    def update_email(self, form):
        user = self.request.user
        # @@@ handle multiple emails per user
        email = form.cleaned_data["email"].strip()
        if not self.primary_email_address:
            user.email = email
            EmailAddress.objects.add_email(self.request.user, email, primary=True)
            user.save()
        else:
            if email != self.primary_email_address.email:
                user.email = email
                self.primary_email_address.email = email
                user.save()
                self.primary_email_address.save()
    
    def update_account(self, form):
        fields = {}
        if "timezone" in form.cleaned_data:
            fields["timezone"] = form.cleaned_data["timezone"]
        if "language" in form.cleaned_data:
            fields["language"] = form.cleaned_data["language"]
        if fields:
            account = self.request.user.account
            for k, v in fields.iteritems():
                setattr(account, k, v)
            account.save()
    
    def get_success_url(self, fallback_url=None):
        if fallback_url is None:
            fallback_url = settings.ACCOUNT_SETTINGS_REDIRECT_URL
        return default_redirect(self.request, fallback_url)
