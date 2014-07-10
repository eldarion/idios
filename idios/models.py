from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

from account.signals import user_logged_in

from .utils import get_profile_model, get_profile_form


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

    def get_absolute_url(self):
        from .conf import settings
        if len(settings.IDIOS_PROFILE_MODULES) > 1:
            # @@@ using PK here is kind of ugly. the alternative is to
            # generate a unique slug for each profile, which is tricky
            kwargs = {
                "profile_slug": self.profile_slug,
                "pk": self.pk
            }
        else:
            if settings.IDIOS_USE_USERNAME:
                kwargs = {"username": self.user.username}
            else:
                kwargs = {"pk": self.pk}
        return reverse("profile_detail", kwargs=kwargs)

    @classmethod
    def get_form(cls):
        return get_profile_form(cls)

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
user_logged_in.connect(additional_info_kickstart)
