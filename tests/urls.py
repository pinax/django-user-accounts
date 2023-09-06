import django
if django.VERSION >= (4, 0):
    from django.urls import include, re_path as url
else:
    from django.conf.urls import include, url

urlpatterns = [
    url(r"^", include("account.urls")),
]
