from django.conf import settings
from django.contrib.sites.models import Site, RequestSite
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpRequest
from django.test import TestCase

from account.utils import get_current_site

class SiteCurrentTests(TestCase):
    
    def setUp(self):
        Site(id=settings.SITE_ID, domain="example.com", name="example.com").save()
        Site(domain="example2.com", name="example2.com").save()
            
    def test_get_current_site(self):
        
        request = HttpRequest()
        request.META = {
            "SERVER_NAME": u"example2.com",
            "SERVER_PORT": "80",
        }
        site = get_current_site(request)
        self.assertTrue(isinstance(site, Site))
        self.assertEqual(site.name, u"example2.com")

        site.delete()
        
        self.assertRaises(Http404, get_current_site, request, raise404=True)

        site = get_current_site(request)
        self.assertEqual(site.id, settings.SITE_ID)
        self.assertEqual(site.name, u"example.com")