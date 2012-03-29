import urlparse

from django.core import urlresolvers
from django.http import HttpResponseRedirect, QueryDict
from django.utils.decorators import method_decorator

from account.conf import settings


class LoginRequiredMixin(object):
    
    redirect_field_name = "next"
    login_url = None
    
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if request.user.is_authenticated():
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
        redirect_to = self.get_login_url()
        try:
            redirect_url = urlresolvers.reverse(redirect_to)
        except urlresolvers.NoReverseMatch:
            if callable(redirect_to):
                raise
            if "/" not in redirect_to and "." not in redirect_to:
                raise
        next = self.get_next_url()
        url_bits = list(urlparse.urlparse(redirect_url))
        if self.redirect_field_name:
            querystring = QueryDict(url_bits[4], mutable=True)
            querystring[self.redirect_field_name] = next
            url_bits[4] = querystring.urlencode(safe="/")
        return HttpResponseRedirect(urlparse.urlunparse(url_bits))
    
    def get_login_url(self):
        return self.login_url or settings.ACCOUNT_LOGIN_URL
    
    def get_next_url(self):
        return self.request.get_full_path()
