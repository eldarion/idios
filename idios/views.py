import json

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django.contrib.auth.models import User

from account.mixins import LoginRequiredMixin

from .conf import settings
from .utils import get_profile_model, get_profile_base


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
        search_terms = self.request.GET.get("search", "")
        order = self.request.GET.get("order", "date")

        ctx = {
            "order": order,
            "search_terms": search_terms,
        }
        ctx.update(super(ProfileListView, self).get_context_data(**kwargs))

        return ctx


class ProfileDetailView(DetailView):

    template_name = "idios/profile.html"
    context_object_name = "profile"

    def get_object(self):
        profile_class = get_profile_model(self.kwargs.get("profile_slug"))

        if profile_class is None:
            raise Http404

        if settings.IDIOS_USE_USERNAME:
            self.page_user = get_object_or_404(User, username=self.kwargs["username"])
            profile = get_object_or_404(profile_class, user=self.page_user)
        else:
            profile = get_object_or_404(profile_class, pk=self.kwargs["pk"])
            self.page_user = profile.user

        if not self.request.user.has_perm("can_view", obj=profile):
            raise Http404

        return profile

    def get_context_data(self, **kwargs):
        base_profile_class = get_profile_base()
        profiles = base_profile_class.objects.filter(user=self.page_user)

        is_me = self.request.user == self.page_user

        ctx = {
            "is_me": is_me,
            "page_user": self.page_user,
            "profiles": profiles,
        }
        ctx.update(super(ProfileDetailView, self).get_context_data(**kwargs))

        return ctx


class ProfileCreateView(LoginRequiredMixin, CreateView):

    template_name = "idios/profile_create.html"
    template_name_ajax = "idios/profile_create_ajax.html"

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.template_name_ajax]
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
        ctx = super(ProfileCreateView, self).get_context_data(**kwargs)
        ctx["profile_form"] = ctx["form"]
        return ctx

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return self.object.get_absolute_url()


class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    template_name = "idios/profile_edit.html"
    template_name_ajax = "idios/profile_edit_ajax.html"
    template_name_ajax_success = "idios/profile_edit_ajax_success.html"
    context_object_name = "profile"

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.template_name_ajax]
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
        ctx = super(ProfileUpdateView, self).get_context_data(**kwargs)
        ctx["profile_form"] = ctx["form"]
        return ctx

    def form_valid(self, form):
        self.object = form.save()
        if self.request.is_ajax():
            data = {
                "status": "success",
                "location": self.object.get_absolute_url(),
                "html": render_to_string(self.template_name_ajax_success),
            }
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.is_ajax():
            ctx = RequestContext(self.request, self.get_context_data(form=form))
            data = {
                "status": "failed",
                "html": render_to_string(self.template_name_ajax, ctx),
            }
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return self.object.get_absolute_url()
