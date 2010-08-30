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

from idios import settings

def get_profile_base():
    """
    Return the profile model class which is the base class for all
    profile models (used for querying on all profiles).

    If multiple-profiles are not in use, this will be the single
    profile model class itself: there is no reason to query on an
    ancestor model in this case.

    If multiple-profiles are in use, this will be the model class
    referenced by the ``IDIOS_PROFILE_BASE`` setting. Normally this
    will be idios' own ``ProfileBase`` model, but some projects may
    have another model class inheriting from ProfileBase and defining
    some additional fields, which all their profile models then
    inherit from in turn.

    If the appropriate setting does not resolve to an actual model,
    raise ``django.contrib.auth.models.SiteProfileNotAvailable``.

    """
    if settings.MULTIPLE_PROFILES:
        module = settings.PROFILE_BASE
    else:
        module = settings.DEFAULT_PROFILE_MODULE
    model = get_model(*module.split('.'))
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
        module = settings.DEFAULT_PROFILE_MODULE
        model = get_model(*module.split('.'))
        if model is None:
            raise SiteProfileNotAvailable
    else:
        for module in settings.PROFILE_MODULES:
            model = get_model(*module.split('.'))
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
            exclude = ("user",) # user will be filled in by the view.
    return _ProfileForm
