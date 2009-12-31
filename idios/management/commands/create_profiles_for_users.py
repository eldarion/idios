from django.conf import settings
from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import User

from idios.models import Profile



class Command(NoArgsCommand):
    help = "Create a profile object for users which do not have one."
    
    def handle_noargs(self, **options):
        for user in User.objects.all():
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                profile.save()
