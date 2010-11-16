from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

import idios
from idios.utils import get_profile_model

try:
    from pinax.apps.account.signals import user_logged_in
except ImportError:
    user_logged_in = None


class ClassProperty(property):
    
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class ProfileBase(models.Model):
    
    # @@@ could be unique=True if subclasses don't inherit a concrete base class
    # @@@ need to look at this more
    user = models.ForeignKey(User, verbose_name=_("user"))
    
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        abstract = True
    
    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self, group=None):
        # @@@ make group-aware
        if idios.settings.MULTIPLE_PROFILES:
            # @@@ using PK here is kind of ugly. the alternative is to
            # generate a unique slug for each profile, which is tricky
            kwargs = {
                "profile_slug": self.profile_slug,
                "profile_pk": self.pk
            }
        else:
            kwargs = {"username": self.user.username}
        return reverse("profile_detail", kwargs=kwargs)
    
    def _default_profile_slug(cls):
        return cls._meta.module_name
    
    profile_slug = ClassProperty(classmethod(_default_profile_slug))


def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = get_profile_model().objects.get_or_create(user=instance)
post_save.connect(create_profile, sender=User)


def additional_info_kickstart(sender, **kwargs):
    request = kwargs.get("request")
    request.session["idios_additional_info_kickstart"] = True
if user_logged_in: # protect against Pinax not being available
    user_logged_in.connect(additional_info_kickstart)
