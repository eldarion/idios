from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

try:
    from pinax.apps.account.signals import user_logged_in
except ImportError:
    user_logged_in = None


class ProfileBase(models.Model):
    
    user = models.ForeignKey(User, unique=True, verbose_name=_("user"))
    
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        abstract = True
    
    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self, group=None):
        # @@@ make group-aware
        return reverse("profile_detail", kwargs={"username": self.user.username})


def additional_info_kickstart(sender, **kwargs):
    request = kwargs.get("request")
    request.session["idios_additional_info_kickstart"] = True
if user_logged_in: # protect against Pinax not being available
    user_logged_in.connect(additional_info_kickstart)