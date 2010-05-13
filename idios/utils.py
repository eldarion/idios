"""
Utility functions for retrieving and generating forms for the
site-specific user profile model specified in the
``AUTH_PROFILE_MODULE`` setting.

This file was pulled from django-profiles as it made the most sense. Slightly
modified for Eldarion standards.

"""
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import get_model

from django.contrib.auth.models import SiteProfileNotAvailable


def get_profile_model():
    """
    Return the model class for the currently-active user profile
    model, as defined by the ``AUTH_PROFILE_MODULE`` setting. If that
    setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    if (not hasattr(settings, "AUTH_PROFILE_MODULE")) or \
           (not settings.AUTH_PROFILE_MODULE):
        raise SiteProfileNotAvailable
    profile_mod = get_model(*settings.AUTH_PROFILE_MODULE.split("."))
    if profile_mod is None:
        raise SiteProfileNotAvailable
    return profile_mod


def get_profile_form():
    """
    Return a form class (a subclass of the default ``ModelForm``)
    suitable for creating/editing instances of the site-specific user
    profile model, as defined by the ``AUTH_PROFILE_MODULE``
    setting. If that setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    profile_mod = get_profile_model()
    class _ProfileForm(forms.ModelForm):
        class Meta:
            model = profile_mod
            exclude = ("user",) # user will be filled in by the view.
    return _ProfileForm


def get_default_redirect(request, redirect_field_name="next",
        login_redirect_urlname=None, session_key_value="redirect_to"):
    """
    Returns the URL to be used in login procedures by looking at different
    values in the following order:
    
    - a REQUEST value, GET or POST, named "next" by default.
    - LOGIN_REDIRECT_URL - the URL in the setting
    - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the settings
    """
    if login_redirect_urlname is None:
        login_redirect_urlname = getattr(settings, "LOGIN_REDIRECT_URLNAME", "")
    if login_redirect_urlname:
        default_redirect_to = reverse(login_redirect_urlname)
    else:
        default_redirect_to = settings.LOGIN_REDIRECT_URL
    redirect_to = request.REQUEST.get(redirect_field_name)
    print redirect_to
    if not redirect_to:
        # try the session if available
        if hasattr(request, "session"):
            redirect_to = request.session.get(session_key_value)
    # light security check -- make sure redirect_to isn't garabage.
    if not redirect_to or "://" in redirect_to or " " in redirect_to:
        redirect_to = default_redirect_to
    return redirect_to