from django.conf import settings
from django.test import TestCase

import idios


# this would make a lovely context manager, but... 2.4 :(
class SettingsTestCase(TestCase):
    setting_overrides = {}
    NOT_FOUND = object()
    
    def _pre_setup(self):
        self._original_settings = {}
        for k,v in self.setting_overrides.items():
            self._original_settings[k] = getattr(settings, k, self.NOT_FOUND)
            if v is self.NOT_FOUND:
                delattr(settings, k)
            else:
                setattr(settings, k, v)
        super(SettingsTestCase, self)._pre_setup()
    
    def _post_teardown(self):
        super(SettingsTestCase, self)._post_teardown()
        for k,v in self._original_settings.items():
            if v is self.NOT_FOUND:
                delattr(settings, k)
            else:
                setattr(settings, k, v)


class IdiosSettingsTestCase(SettingsTestCase):
    def _pre_setup(self):
        super(IdiosSettingsTestCase, self)._pre_setup()
        idios.settings = idios.IdiosSettings()
    
    def _post_teardown(self):
        super(IdiosSettingsTestCase, self)._post_teardown()
        idios.settings = idios.IdiosSettings()
