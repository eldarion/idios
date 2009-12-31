from django.conf import settings
from django import forms

from idios.models import Profile

class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ('user',)
