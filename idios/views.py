from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

try:
    from django.views.generic import ListView, DetailView, CreateView
except ImportError:
    from cbv import ListView, DetailView, CreateView

from idios.utils import get_profile_form, get_profile_model, get_profile_base


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


class ProfileListView(ListView):
    """
    List all profiles of a given type (or the default type, if
    profile_slug is not given.)
    
    If all_profiles is set to True, all profiles are listed.
    """
    template_name = "idios/profiles.html"
    context_object_name = "profiles"
    all_profiles = False
    
    def get_model_class(self):

        # @@@ not group-aware (need to look at moving to profile model)
        profile_slug = self.kwargs.get("profile_slug", None)

        if self.all_profiles:
            profile_class = get_profile_base()
        else:
            profile_class = get_profile_model(profile_slug)

        if profile_class is None:
            raise Http404

        return profile_class

    def get_queryset(self):

        profiles = self.get_model_class().objects.select_related().\
                order_by("-date_joined")
        
        search_terms = self.request.GET.get("search", "")
        order = self.request.GET.get("order", "date")
        
        if search_terms:
            profiles = profiles.filter(user__username__icontains=search_terms)
        if order == "date":
            profiles = profiles.order_by("-user__date_joined")
        elif order == "name":
            profiles = profiles.order_by("user__username")

        return profiles
    
    def get_context_data(self, **kwargs):

        group, bridge = group_and_bridge(self.kwargs)

        search_terms = self.request.GET.get("search", "")
        order = self.request.GET.get("order", "date")

        ctx = group_context(group, bridge)
        ctx.update({
            "order": order,
            "search_terms": search_terms,
        })
        ctx.update(
            super(ProfileListView, self).get_context_data(**kwargs)
        )

        return ctx


class ProfileDetailView(DetailView):

    template_name = "idios/profile.html"
    context_object_name = "profile"
    
    def get_object(self):

        username = self.kwargs.get('username')
        profile_class = get_profile_model(self.kwargs.get('profile_slug'))

        if profile_class is None:
            raise Http404

        if username:
            self.page_user = get_object_or_404(User, username=username)
            return get_object_or_404(profile_class, user=self.page_user)
        else:
            profile = get_object_or_404(
                profile_class, pk=self.kwargs.get('profile_pk')
            )
            self.page_user = profile.user
            return profile
    
    def get_context_data(self, **kwargs):

        base_profile_class = get_profile_base()
        profiles = base_profile_class.objects.filter(user=self.page_user)

        group, bridge = group_and_bridge(kwargs)
        is_me = self.request.user == self.page_user

        ctx = group_context(group, bridge)
        ctx.update({
            "is_me": is_me,
            "page_user": self.page_user,
            "profiles": profiles,
        })
        ctx.update(
            super(ProfileDetailView, self).get_context_data(**kwargs)
        )

        return ctx
    

#NOTE: this lacks backwards compatibility in the sense that the form is
# passed thru the context as 'form' instead of 'profile_form'
class ProfileCreateView(CreateView):

    template_name = "idios/profile_create.html"
    template_name_facebox = "idios/profile_create_facebox.html"
    
    def get_template_names(self):

        if self.request.is_ajax():
            return [self.template_name_facebox]
        else:
            return [self.template_name]

    def get_form_class(self):

        if self.form_class:
            return self.form_class

        profile_class = get_profile_model(self.kwargs.get('profile_slug'))

        if profile_class is None:
            raise Http404

        return get_profile_form(profile_class)

    def form_valid(self, form):

        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        self.object = profile

        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):

        group, bridge = group_and_bridge(self.kwargs)

        ctx = group_context(group, bridge)
        ctx.update(
            super(ProfileCreateView, self).get_context_data(**kwargs)
        )
        return ctx

    def get_success_url(self):

        if self.success_url:
            return self.success_url

        group, bridge = group_and_bridge(self.kwargs)
        return self.object.get_absolute_url(group=group)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileCreateView, self).dispatch(*args, **kwargs)


@login_required
def profile_edit(request, profile_slug=None, **kwargs):
    """
    profile_edit
    """
    template_name = kwargs.pop("template_name", "idios/profile_edit.html")
    form_class = kwargs.pop("form_class", None)
    
    if request.is_ajax():
        template_name = kwargs.get(
            "template_name_facebox",
            "idios/profile_edit_facebox.html"
        )
    
    group, bridge = group_and_bridge(kwargs)
    
    # @@@ not group-aware (need to look at moving to profile model)
    profile_class = get_profile_model(profile_slug)
    if profile_class is None:
        raise Http404
    profile = profile_class.objects.get(user=request.user)
    
    if form_class is None:
        form_class = get_profile_form(profile_class)
    
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
