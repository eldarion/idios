from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
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


def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """
    
    bridge = kwargs.pop("bridge", None)
    
    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }


def profiles(request, **kwargs):
    """
    profiles
    """
    template_name = kwargs.pop("template_name", "idios/profiles.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    # @@@ not group-aware (need to look at moving to profile model)
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
    
    ctx = group_context(group, bridge)
    ctx.update({
        "users": users,
        "order": order,
        "search_terms": search_terms,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def profile(request, username, **kwargs):
    """
    profile
    """
    template_name = kwargs.pop("template_name", "idios/profile.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    # @@@ not group-aware (need to look at moving to profile model)
    other_user = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated():
        if request.user == other_user:
            is_me = True
        else:
            is_me = False
    else:
        is_me = False
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_me": is_me,
        "other_user": other_user,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def profile_edit(request, **kwargs):
    """
    profile_edit
    """
    template_name = kwargs.pop("template_name", "idios/profile_edit.html")
    form_class = kwargs.pop("form_class", None)
    
    if form_class is None:
        form_class = get_profile_form()
    
    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "idios/profile_edit_facebox.html"
        )
    
    group, bridge = group_and_bridge(kwargs)
    
    # @@@ not group-aware (need to look at moving to profile model)
    profile = request.user.get_profile()
    
    if request.method == "POST":
        profile_form = form_class(request.POST, instance=profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            return HttpResponseRedirect(profile.get_absolute_url(group=group))
    else:
        profile_form = form_class(instance=profile)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "profile": profile,
        "profile_form": profile_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))
