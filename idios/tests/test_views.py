from django.test import TestCase

from django.contrib.auth.models import User, SiteProfileNotAvailable
from django.core.urlresolvers import reverse

from idios import utils
from idios.tests.utils import IdiosSettingsTestCase
from idios.tests.models import SimpleProfile, SecretIdentityProfile, SecretVillainProfile


__all__ = ["TestViews", "TestViewsMultiProfiles"]


class TestViews(IdiosSettingsTestCase):
    
    fixtures = ["test_idios"]
    
    def test_profiles(self):
        response = self.client.get(reverse("profile_list"))
        self.assertEqual(response.template.name, "idios/profiles.html")
        self.assertEqual(
            [str(p) for p in response.context["profiles"]],
            ["bob", "joe"]
        )
    
    def test_profile(self):
        response = self.client.get(
            reverse("profile_detail", kwargs={"username": "joe"})
        )
        self.assertEqual(response.template.name, "idios/profile.html")
        self.assertEqual(str(response.context["profile"]), "joe")
    
    def test_edit_profile(self):
        logged_in = self.client.login(username="joe", password="test")
        self.assert_(logged_in)
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("profile_edit"), {"name": "Joe Doe"}
        )
        self.assertRedirects(response, "/profiles/profile/joe/")
        self.assertEqual(
            SimpleProfile.objects.get(user__username="joe").name,
            "Joe Doe"
        )
    
    def test_nonexistent_profile_slug_returns_404(self):
        logged_in = self.client.login(username="joe", password="test")
        self.assert_(logged_in)
        for url_name in ["profile_list", "profile_edit", "profile_create"]:
            url = reverse(url_name, kwargs={"profile_slug": "bad"})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)


class TestViewsMultiProfiles(TestViews):
    fixtures = ["test_idios"]
    setting_overrides = {
        "IDIOS_PROFILE_MODULES": ["tests.SecretIdentityProfile"],
        "IDIOS_PROFILE_BASE": "tests.SecretIdentityProfile"
    }
    
    def test_non_default_profiles(self):
        profile = SecretIdentityProfile.objects.create(
            user=User.objects.get(username="joe"),
            super_power="x-ray vision"
        )
        response = self.client.get(
            reverse("profile_list", kwargs={"profile_slug": "secret"})
        )
        self.assertEqual(response.template.name, "idios/profiles.html")
        self.assertEqual(len(response.context["profiles"]), 1)
        self.assertEqual(response.context["profiles"][0], profile)
    
    def test_all_profiles(self):
        profile1 = SecretIdentityProfile.objects.create(
            user=User.objects.get(username="joe"),
            super_power="x-ray vision"
        )
        profile2 = SecretVillainProfile.objects.create(
            user=User.objects.get(username="bob"),
            super_power="cackling",
            fiendish_plot="world domination"
        )
        response = self.client.get(reverse("profile_list_all"))
        self.assertEqual(response.template.name, "idios/profiles.html")
        self.assertEqual(
            [p.super_power for p in response.context["profiles"]],
            ["x-ray vision", "cackling"]
        )
    
    def test_alternative_profile(self):
        profile = SecretIdentityProfile.objects.create(
            user=User.objects.get(username="joe"),
            super_power="x-ray vision"
        )
        response = self.client.get(
            reverse("profile_detail", kwargs={
                "profile_slug": "secret",
                "profile_pk": profile.pk
            })
        )
        self.assertEqual(response.template.name, "idios/profile.html")
        self.assertEqual(
            response.context["profile"].super_power,
            "x-ray vision"
        )
    
    def test_edit_profile(self):
        logged_in = self.client.login(username="joe", password="test")
        self.assert_(logged_in)
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("profile_edit"),
            {"name": "Joe Doe"}
        )
        profile = SimpleProfile.objects.get(user__username="joe")
        self.assertRedirects(response, "/profiles/simpleprofile/profile/%s/" % profile.pk)
        self.assertEqual(profile.name, "Joe Doe")
    
    def test_edit_alternative_profile(self):
        profile = SecretIdentityProfile.objects.create(
            user=User.objects.get(username="joe"),
            super_power="x-ray vision"
        )
        logged_in = self.client.login(username="joe", password="test")
        self.assert_(logged_in)
        url = reverse("profile_edit", kwargs={"profile_slug": "secret"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {"super_power": "night vision"})
        self.assertRedirects(response, "/profiles/secret/profile/%s/" % profile.pk)
        self.assertEqual(
            SecretIdentityProfile.objects.get(user__username="joe").super_power,
            "night vision"
        )
    
    def test_create_profile(self):
        logged_in = self.client.login(username="joe", password="test")
        self.assert_(logged_in)
        url = reverse("profile_create", kwargs={"profile_slug": "secret"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {"super_power": "night vision"})
        profile = SecretIdentityProfile.objects.get(user__username="joe")
        self.assertRedirects(response, "/profiles/secret/profile/%s/" % profile.pk)
        self.assertEqual(profile.super_power, "night vision")
