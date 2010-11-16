from django.test import TestCase

from django.contrib.auth.models import SiteProfileNotAvailable

from idios import utils
from idios.tests.utils import IdiosSettingsTestCase
from idios.tests.models import SimpleProfile, SecretIdentityProfile


__all__ = [
    "TestUtils",
    "TestUtilsNoProfile",
    "TestUtilsMultiProfiles",
    "TestUtilsMultiProfilesBase"
]


class TestUtils(TestCase):
    
    def test_get_profile_base(self):
        """
        In a single-profile configuration, the profile base is the
        default profile.
        
        """
        self.assert_(utils.get_profile_base() is SimpleProfile)
    
    def test_get_profile_model(self):
        self.assert_(utils.get_profile_model() is SimpleProfile)
    
    def test_invalid_profile_model(self):
        utils.idios.settings.DEFAULT_PROFILE_MODULE = "tests.NonExistentProfile"
        self.assertRaises(SiteProfileNotAvailable, utils.get_profile_model)
        utils.idios.settings.DEFAULT_PROFILE_MODULE = "tests.SimpleProfile"
    
    def test_profile_form(self):
        form_class = utils.get_profile_form()
        form = form_class(data={})
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors["name"], [u"This field is required."])


class TestUtilsNoProfile(IdiosSettingsTestCase):
    
    setting_overrides = {"AUTH_PROFILE_MODULE": None}
    
    def test_no_profile_model(self):
        self.assertRaises(SiteProfileNotAvailable, utils.get_profile_model)


class TestUtilsMultiProfiles(IdiosSettingsTestCase):
    
    setting_overrides = {
        "IDIOS_PROFILE_MODULES": ["tests.SecretIdentityProfile"]
    }
    
    def test_get_profile_base(self):
        """
        In a multi-profile configuration without IDIOS_PROFILE_BASE,
        the profile base is the default profile.
        
        """
        self.assert_(utils.get_profile_base() is SimpleProfile)
    
    def test_get_default_profile_model(self):
        self.assert_(utils.get_profile_model() is SimpleProfile)
    
    def test_get_alt_profile_model(self):
        self.assert_(utils.get_profile_model("secret") is SecretIdentityProfile)
    
    def test_get_invalid_profile_model(self):
        self.assertEqual(utils.get_profile_model("doesntexist"), None)
    
    def test_alt_profile_form(self):
        form_class = utils.get_profile_form(SecretIdentityProfile)
        form = form_class(data={})
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors["super_power"], [u"This field is required."])


class TestUtilsMultiProfilesBase(IdiosSettingsTestCase):
    setting_overrides = {
        "IDIOS_PROFILE_MODULES": ["tests.SecretIdentityProfile"],
        "IDIOS_PROFILE_BASE": "tests.SecretIdentityProfile"
    }
    
    def test_get_profile_base(self):
        self.assert_(utils.get_profile_base() is SecretIdentityProfile)
    
    def test_invalid_profile_base(self):
        utils.idios.settings.PROFILE_BASE = "tests.NonExistentProfile"
        self.assertRaises(SiteProfileNotAvailable, utils.get_profile_base)
        utils.idios.settings.PROFILE_BASE = "tests.SecretIdentityProfile"
