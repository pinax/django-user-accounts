from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.contrib import auth

from account.conf import settings
from account.forms import SignupForm, LoginUsernameForm
from account.utils import default_redirect


class SignupView(FormView):
    
    template_name = "account/signup.html"
    form_class = SignupForm


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
