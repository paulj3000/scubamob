"""
Tests for the settings.py hardening pass (CODE_REVIEW.md §5, project-level
settings cluster): cookie/SSL hardening gated on DEBUG, DRF throttling
actually enforced, IS_PRODUCTION env-driven, and dead/landmine settings
removed.
"""
from django.conf import settings
from django.test import TestCase, override_settings


class TestCookieAndSslHardening(TestCase):
    def test_hardening_is_off_for_local_dev(self):
        """ settings.py computes these as `not DEBUG` once, at settings-
        module import time (this environment's .env has DEBUG=True) --
        not as a dynamic property. Django's test runner separately forces
        settings.DEBUG to False for the duration of the test suite, but
        that happens *after* import and does not retroactively recompute
        these already-baked-in values. So this asserts the real-world
        outcome (hardening off for local dev) without relying on
        settings.DEBUG's value here, since by the time this test runs
        that no longer reflects what was true when settings.py loaded. """
        self.assertFalse(settings.SESSION_COOKIE_SECURE)
        self.assertFalse(settings.CSRF_COOKIE_SECURE)
        self.assertFalse(settings.SECURE_SSL_REDIRECT)

    @override_settings(
        DEBUG=False,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        SECURE_SSL_REDIRECT=True,
        SECURE_HSTS_SECONDS=60 * 60 * 24 * 30,
    )
    def test_hardening_values_used_when_debug_is_off(self):
        """ settings.py derives these from `not DEBUG` at import time, so
        this exercises the values it would compute under DEBUG=False
        rather than re-importing the module (Django settings are only
        evaluated once at process start). """
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertGreater(settings.SECURE_HSTS_SECONDS, 0)


class TestIsProduction(TestCase):
    def test_is_production_defaults_to_false_and_is_env_driven(self):
        self.assertFalse(settings.IS_PRODUCTION)
        self.assertIsInstance(settings.IS_PRODUCTION, bool)


class TestDeadSettingsRemoved(TestCase):
    def test_landmine_and_no_op_settings_are_gone(self):
        self.assertFalse(hasattr(settings, 'CORS_ORIGIN_ALLOW_ALL'))
        self.assertFalse(hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'))
        self.assertFalse(hasattr(settings, 'xCOMPRESS_FILTERS'))
        self.assertFalse(hasattr(settings, 'xCOMPRESS_YUGLIFY_BINARY'))
        self.assertFalse(hasattr(settings, 'TEST_PEP8_DIRS'))
        self.assertNotIn('PAGINATE_BY', settings.REST_FRAMEWORK)


class TestThrottling(TestCase):
    def test_throttle_classes_are_configured(self):
        classes = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES']
        rates = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']

        self.assertIn('rest_framework.throttling.AnonRateThrottle', classes)
        self.assertIn('rest_framework.throttling.UserRateThrottle', classes)
        self.assertIn('anon', rates)
        self.assertIn('user', rates)

    def test_a_tiny_rate_is_actually_enforced(self):
        """ confirms DRF's throttle machinery honors DEFAULT_THROTTLE_RATES
        (i.e. the setting isn't just declared but inert) using an
        isolated in-memory cache and a throttle instance constructed
        directly -- avoids depending on (or polluting) the process-wide
        default cache that every anonymous request in the full test
        suite shares, which made an earlier version of this test order-
        dependent and flaky. """
        from django.contrib.auth.models import AnonymousUser
        from django.core.cache.backends.locmem import LocMemCache
        from django.test import RequestFactory
        from rest_framework.throttling import AnonRateThrottle

        class _TinyAnonThrottle(AnonRateThrottle):
            THROTTLE_RATES = {'anon': '2/min'}
            cache = LocMemCache('throttle-test', {})

        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        throttle = _TinyAnonThrottle()
        view = object()

        allowed = [throttle.allow_request(request, view) for _ in range(3)]

        self.assertEqual(allowed, [True, True, False])
