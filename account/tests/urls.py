import django
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

# D 2.0 compatibility
if django.VERSION[0] < 2:
    admin_urls = url(r"admin/", include(admin.site.urls))
else:
    admin_urls = url(r"admin/", admin.site.urls)


urlpatterns = [
    admin_urls,
    url(r"^", include("account.urls")),
]
