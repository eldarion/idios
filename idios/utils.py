"""
Utility functions for retrieving and generating forms for the
site-specific user profile model specified in the
``AUTH_PROFILE_MODULE`` setting.

This file was pulled from django-profiles as it made the most sense. Slightly
modified for Eldarion standards.

"""
from django import forms
from django.conf import settings
from django.db.models import get_model

from django.contrib.auth.models import SiteProfileNotAvailable


def get_profile_model(profile_slug=None):
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting. If that
    setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    if profile_slug is None:
        if (not hasattr(settings, "AUTH_PROFILE_MODULE")) or \
               (not settings.AUTH_PROFILE_MODULE):
            raise SiteProfileNotAvailable
        module = settings.AUTH_PROFILE_MODULE
    else:
        if (not hasattr(settings, "IDIOS_PROFILE_MODULES")) or \
               (not settings.IDIOS_PROFILE_MODULES) or \
               (not settings.IDIOS_PROFILE_MODULES.get(profile_slug)):
            raise SiteProfileNotAvailable
        module = settings.IDIOS_PROFILE_MODULES.get(profile_slug).get("model")
    profile_mod = get_model(*module.split("."))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod


def get_profile_form(profile_slug):
    """
    Return a form class (a subclass of the default ``ModelForm``)
    suitable for creating/editing instances of the site-specific user
    profile model, as defined by the ``AUTH_PROFILE_MODULE``
    setting. If that setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    profile_mod = get_profile_model(profile_slug)
    class _ProfileForm(forms.ModelForm):
        class Meta:
            model = profile_mod
            exclude = ("user",) # user will be filled in by the view.
    return _ProfileForm
