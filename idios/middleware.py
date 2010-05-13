import re

from django import forms
from django.conf import settings
from django.db import models
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_protect

from idios.utils import get_profile_model


class AdditionalInfoMiddleware(object):
    
    def process_request(self, request):
        exemptions = [
            r"^%s" % settings.MEDIA_URL,
            r"^%s" % settings.STATIC_URL,
            r"^/__debug__",
            r"^/account", # @@@ hack for now
        ]
        for exemption in exemptions:
            if re.match(exemption, request.path):
                return None
        kickstart = request.session.get("idios_additional_info_kickstart")
        if kickstart:
            return handle_additional_info(request)


@csrf_protect
def handle_additional_info(request):
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        missing_fields = []
        # look for fields which are required on the model
        for field in profile.idios_required_fields():
            name = isinstance(field, tuple) and field[0] or field
            db_field = profile._meta.get_field(name)
            value = getattr(profile, db_field.attname)
            if isinstance(db_field, (models.CharField, models.TextField)):
                missing = not value
            else:
                missing = value is None
            if missing:
                if not isinstance(field, tuple):
                    missing_fields.append((field, db_field.formfield()))
                else:
                    missing_fields.append(field)
        if not missing_fields:
            return None
        attrs = {}
        for field in missing_fields:
            attrs[field[0]] = field[1]
        AdditionalInfoForm = type("AdditionalInfoForm", (forms.Form,), attrs)
        if request.method == "POST":
            form = AdditionalInfoForm(request.POST, request.FILES)
            if form.is_valid():
                request.session.pop("idios_additional_info_kickstart", None)
                for field, value in form.cleaned_data.iteritems():
                    setattr(profile, field, value)
                profile.save()
                return redirect(request.path)
        else:
            form = AdditionalInfoForm()
        ctx = {
            "form": form,
        }
        return render_to_response(
            "idios/additional_info.html",
            RequestContext(request, ctx)
        )
