"""
Combine the settings ``AUTH_PROFILE_MODULE`` and
``IDIOS_PROFILE_MODULES`` into a single ``PROFILE_MODULES`` list.

``MULTIPLE_PROFILES`` is True if there is more than one profile model
defined, False otherwise.

``DEFAULT_PROFILE_MODULE`` is the profile model referenced by
``AUTH_PROFILE_MODULE``, or the first one listed in
``IDIOS_PROFILE_MODULES``.

This module also sets a default value of "idios.ProfileBase" for the
``IDIOS_PROFILE_BASE`` setting.

"""

from django.conf import settings


PROFILE_MODULES= []

modules = []
mod = getattr(settings, 'AUTH_PROFILE_MODULE', None)
if mod:
    modules.append(mod)

DEFAULT_PROFILE_MODULE = None
    
for module in modules + getattr(settings, 'IDIOS_PROFILE_MODULES', []):
    if DEFAULT_PROFILE_MODULE is None:
        DEFAULT_PROFILE_MODULE = module
    PROFILE_MODULES.append(module)

MULTIPLE_PROFILES = len(PROFILE_MODULES) > 1

PROFILE_BASE = getattr(settings, 'IDIOS_PROFILE_BASE', 'idios.ProfileBase')
