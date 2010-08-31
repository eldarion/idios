from django.conf import settings as django_settings


class IdiosSettings(object):
    """
    Combine the settings ``AUTH_PROFILE_MODULE`` and
    ``IDIOS_PROFILE_MODULES`` into a single ``PROFILE_MODULES`` list.

    ``MULTIPLE_PROFILES`` is True if there is more than one profile model
    defined, False otherwise.

    ``DEFAULT_PROFILE_MODULE`` is the profile model referenced by
    ``AUTH_PROFILE_MODULE``, or the first one listed in
    ``IDIOS_PROFILE_MODULES``.

    """
    def __init__(self):
        self.PROFILE_MODULES= []

        modules = []
        mod = getattr(django_settings, 'AUTH_PROFILE_MODULE', None)
        if mod:
            modules.append(mod)

        self.DEFAULT_PROFILE_MODULE = None
        
        for module in modules + getattr(django_settings,
                                        'IDIOS_PROFILE_MODULES', []):
            if self.DEFAULT_PROFILE_MODULE is None:
                self.DEFAULT_PROFILE_MODULE = module
            self.PROFILE_MODULES.append(module)

        self.MULTIPLE_PROFILES = len(self.PROFILE_MODULES) > 1

        self.PROFILE_BASE = getattr(django_settings, 'IDIOS_PROFILE_BASE', None)
        

settings = IdiosSettings()
