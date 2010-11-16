VERSION = (0, 2, 0, "a", 1) # following PEP 386
DEV_N = 1
POST_N = 0


def build_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "f":
        version = "%s%s%s" % (version, VERSION[3], VERSION[4])
        if DEV_N:
            version = "%s.dev%s" % (version, DEV_N)
    elif POST_N > 0:
        version = "%s.post%s" % (version, POST_N)
    return version


__version__ = build_version()


try:
    import django
except ImportError:
    django = None
else:
    from django.utils.functional import LazyObject

if django:
    class IdiosLazySettings(LazyObject):
        
        def _setup(self):
            self._wrapped = IdiosSettings()
    
    
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
            from django.conf import settings
            
            self.PROFILE_MODULES = []
            
            modules = []
            mod = getattr(settings, "AUTH_PROFILE_MODULE", None)
            if mod:
                modules.append(mod)
            
            self.DEFAULT_PROFILE_MODULE = None
            
            for module in modules + getattr(settings, "IDIOS_PROFILE_MODULES", []):
                if self.DEFAULT_PROFILE_MODULE is None:
                    self.DEFAULT_PROFILE_MODULE = module
                self.PROFILE_MODULES.append(module)
            
            self.MULTIPLE_PROFILES = len(self.PROFILE_MODULES) > 1
            self.PROFILE_BASE = getattr(settings, "IDIOS_PROFILE_BASE", None)
    
    settings = IdiosLazySettings()
