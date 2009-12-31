from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from idios.utils import get_profile_form



if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None



def profiles(request, template_name="idios/profiles.html"):
    
    users = User.objects.all().order_by("-date_joined")
    
    search_terms = request.GET.get("search", "")
    order = request.GET.get("order")
    
    if not order:
        order = "date"
    if search_terms:
        users = users.filter(username__icontains=search_terms)
    if order == "date":
        users = users.order_by("-date_joined")
    elif order == "name":
        users = users.order_by("username")
    
    return render_to_response(template_name, {
        "users": users,
        "order": order,
        "search_terms": search_terms,
    }, context_instance=RequestContext(request))


def profile(request, username, template_name="idios/profile.html"):
    
    other_user = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated():
        if request.user == other_user:
            is_me = True
        else:
            is_me = False
    else:
        is_me = False
    
    return render_to_response(template_name, {
        "is_me": is_me,
        "other_user": other_user,
    }, context_instance=RequestContext(request))


@login_required
def profile_edit(request, **kwargs):
    
    template_name = kwargs.get("template_name", "idios/profile_edit.html")
    form_class = kwargs.get("form_class")
    
    if form_class is None:
        form_class = get_profile_form()
    
    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "idios/profile_edit_facebox.html"
        )
    
    profile = request.user.get_profile()
    
    if request.method == "POST":
        profile_form = form_class(request.POST, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            redirect_to = reverse("profile_detail", args=[request.user.username])
            return HttpResponseRedirect(redirect_to)
    else:
        profile_form = form_class(instance=profile)
    
    return render_to_response(template_name, {
        "profile": profile,
        "profile_form": profile_form,
    }, context_instance=RequestContext(request))
