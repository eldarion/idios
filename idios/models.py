from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User



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
