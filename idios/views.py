from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

try:
    from django.views.generic import ListView, DetailView, CreateView, UpdateView
except ImportError:
    try:
        from cbv import ListView, DetailView, CreateView, UpdateView
    except ImportError:
        raise ImportError(
            "It appears you are running a version of Django < "
            "1.3. To use idios with this version of Django, install "
            "django-cbv==0.1.5."
        )

from idios.utils import get_profile_model, get_profile_base


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
        
        profiles = self.get_model_class().objects.select_related()
        profiles = profiles.order_by("-date_joined")
        
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
        
        username = self.kwargs.get("username")
        profile_class = get_profile_model(self.kwargs.get("profile_slug"))
        
        if profile_class is None:
            raise Http404
        
        if username:
            self.page_user = get_object_or_404(User, username=username)
            return get_object_or_404(profile_class, user=self.page_user)
        else:
            profile = get_object_or_404(
                profile_class, pk=self.kwargs.get("profile_pk")
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
        
        profile_class = get_profile_model(self.kwargs.get("profile_slug"))
        
        if profile_class is None:
            raise Http404
        
        return profile_class.get_form()
    
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
        ctx["profile_form"] = ctx["form"]
        return ctx
    
    def get_success_url(self):
        
        if self.success_url:
            return self.success_url
        
        group, bridge = group_and_bridge(self.kwargs)
        return self.object.get_absolute_url(group=group)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileCreateView, self).dispatch(*args, **kwargs)


class ProfileUpdateView(UpdateView):
    
    template_name = "idios/profile_edit.html"
    template_name_facebox = "idios/profile_edit_facebox.html"
    context_object_name = "profile"
    
    def get_template_names(self):
        if self.request.is_ajax():
            return [self.template_name_facebox]
        else:
            return [self.template_name]
    
    def get_form_class(self):
        
        if self.form_class:
            return self.form_class
        
        profile_class = get_profile_model(self.kwargs.get("profile_slug"))
        
        if profile_class is None:
            raise Http404
        
        return profile_class.get_form()
    
    def get_object(self, queryset=None):
        
        profile_class = get_profile_model(self.kwargs.get("profile_slug"))
        if profile_class is None:
            raise Http404
        
        profile = profile_class.objects.get(user=self.request.user)
        return profile
    
    def get_context_data(self, **kwargs):
        
        group, bridge = group_and_bridge(self.kwargs)
        ctx = group_context(group, bridge)
        ctx.update(
            super(ProfileUpdateView, self).get_context_data(**kwargs)
        )
        ctx["profile_form"] = ctx["form"]
        return ctx
    
    def get_success_url(self):
    
        if self.success_url:
            return self.success_url
        
        group, bridge = group_and_bridge(self.kwargs)
        return self.object.get_absolute_url(group=group)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileUpdateView, self).dispatch(*args, **kwargs)
