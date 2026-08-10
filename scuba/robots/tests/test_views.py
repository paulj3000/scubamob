"""
Tests for scuba.robots.views.RuleList (CODE_REVIEW.md §5, `scuba/robots`).

The custom Settings.__getattr__ proxy in scuba/robots/settings.py never
raised AttributeError for unknown names, so every hasattr(settings, ...)
check in this file was unconditionally True regardless of the actual
configured value. Concretely, get_current_site() always did a host-based
Site.objects.get(domain=request.get_host()) lookup even though
ROBOTS_SITE_BY_REQUEST defaults to (and, in this project, is always) off
-- which 500s the public /robots.txt the moment a request's Host header
doesn't exactly match a registered Site domain (e.g. behind a load
balancer).
"""
from django.test import TestCase, override_settings

UNREGISTERED_HOST = 'some-host-nobody-registered.example.com'


class TestRobotsTxt(TestCase):
    @override_settings(ALLOWED_HOSTS=[UNREGISTERED_HOST])
    def test_does_not_crash_when_host_header_does_not_match_any_site(self):
        """ ROBOTS_SITE_BY_REQUEST is not configured (defaults to False),
        so this must fall back to Site.objects.get_current() rather than
        a host-based lookup -- a Host header that matches no registered
        Site must not 500. ALLOWED_HOSTS is overridden purely so the
        request reaches the view at all (Django's own host-header
        validation would otherwise reject it first); the point under
        test is what scuba.robots does *after* that, not ALLOWED_HOSTS
        itself. """
        response = self.client.get('/robots.txt', HTTP_HOST=UNREGISTERED_HOST)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
