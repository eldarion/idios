"""
Utility functions for retrieving and generating forms for the
site-specific user profile model specified in the
``AUTH_PROFILE_MODULE`` or ``IDIOS_PROFILE_MODULES`` settings.

This file was pulled from django-profiles as it made the most sense. Slightly
modified for Eldarion standards.

"""
from django import forms
from django.db.models import get_model

from django.contrib.auth.models import SiteProfileNotAvailable

import idios


def get_profile_base():
    """
    Return a profile model class which is a concrete base class for
    all profile models (used for querying on all profiles).
    
    If multiple-profiles are not in use, this will be the single
    profile model class itself.
    
    If multiple-profiles are in use, this will be the model class
    referenced by the ``IDIOS_PROFILE_BASE`` setting.  If
    ``IDIOS_PROFILE_BASE`` is not set (some projects may not have a
    concrete base class for all profile classes), then querying all
    profiles is not possible, and the all-profiles view will simply
    query the default profile model. (Idios' own ``ProfileBase`` is
    abstract and thus non-queryable.)
    
    If the appropriate setting does not resolve to an actual model,
    raise ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    if idios.settings.MULTIPLE_PROFILES and idios.settings.PROFILE_BASE:
        module = idios.settings.PROFILE_BASE
    else:
        module = idios.settings.DEFAULT_PROFILE_MODULE
    model = get_model(*module.split("."))
    if model is None:
        raise SiteProfileNotAvailable
    return model


def get_profile_model(profile_slug=None):
    """
    Return the model class for the profile module identified by the
    given ``profile_slug``, as defined in the ``AUTH_PROFILE_MODULE``
    or ``IDIOS_PROFILE_MODULES`` settings.
    
    If ``profile_slug`` is not provided, return the default profile
    model.
    
    If no matching profile model is found, return None.
    
    If no default profile model is found, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    if profile_slug is None:
        module = idios.settings.DEFAULT_PROFILE_MODULE
        if module is None:
            raise SiteProfileNotAvailable
        model = get_model(*module.split("."))
        if model is None:
            raise SiteProfileNotAvailable
    else:
        for module in idios.settings.PROFILE_MODULES:
            model = get_model(*module.split("."))
            if model and profile_slug == model.profile_slug:
                break
            else:
                model = None
    return model


def get_profile_form(profile_model=None):
    """
    Return a form class (a subclass of the default ``ModelForm``)
    suitable for creating/editing instances of the given user profile
    model.
    
    """
    if profile_model is None:
        profile_model = get_profile_model()
    class _ProfileForm(forms.ModelForm):
        class Meta:
            model = profile_model
            exclude = ["user"] # user will be filled in by the view.
    return _ProfileForm
