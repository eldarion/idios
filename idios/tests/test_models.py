# from django.test import TestCase
#
# from django.contrib.auth.models import User
#
# from .models import SimpleProfile, SecretIdentityProfile


# class TestProfileBase(TestCase):

#     def setUp(self):
#         User.objects.create(username="bob")
#         User.objects.create(username="joe")

#     def test_auto_created(self):
#         self.assertEqual(User.objects.count(),
#                          SimpleProfile.objects.count())

#     def test_get_absolute_url(self):
#         print User.objects.count(), SimpleProfile.objects.count()
#         p = SimpleProfile.objects.get(user__username="joe")
#         self.assertEqual(p.get_absolute_url(), "/profiles/profile/joe/")

#     def test_default_profile_slug(self):
#         self.assertEqual(SimpleProfile.profile_slug, "simpleprofile")

#     def test_unicode(self):
#         p = SimpleProfile.objects.get(user__username="joe")
#         self.assertEqual(unicode(p), "joe")


# class TestProfileBaseMultiProfiles(TestCase):

#     setting_overrides = {
#         "IDIOS_PROFILE_MODULES": ["tests.SecretIdentityProfile"]
#     }

#     def setup(self):
#         User.objects.create(username="bob")
#         User.objects.create(username="joe")

#     def test_non_default_profile_not_auto_created(self):
#         self.assertEqual(SecretIdentityProfile.objects.count(), 0)

#     def test_get_absolute_url_default_profile(self):
#         p = SimpleProfile.objects.get(user__username="joe")
#         self.assertEqual(
#             p.get_absolute_url(),
#             "/profiles/simpleprofile/profile/%s/" % p.pk
#         )

#     def test_get_absolute_url_alternate_profile(self):
#         p = SecretIdentityProfile.objects.create(user=User.objects.get(username="joe"))
#         self.assertEqual(
#             p.get_absolute_url(),
#             "/profiles/secret/profile/%s/" % p.pk
#         )

#     def test_override_profile_slug(self):
#         self.assertEqual(SecretIdentityProfile.profile_slug, "secret")
