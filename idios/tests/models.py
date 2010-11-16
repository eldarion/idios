from django.db import models

from idios.models import ProfileBase


class SimpleProfile(ProfileBase):
    
    name = models.CharField(max_length=100)


class SecretIdentityProfile(ProfileBase):
    super_power = models.CharField(max_length=100)
    profile_slug = "secret"


class SecretVillainProfile(SecretIdentityProfile):
    
    fiendish_plot = models.CharField(max_length=100)
