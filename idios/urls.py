from django.conf.urls.defaults import patterns, url

import idios
from idios.views import ProfileListView, ProfileDetailView, ProfileUpdateView, ProfileCreateView


if not idios.settings.USE_USERNAME:
    profile_detail_default = url(r"^profile/(?P<pk>\d+)/$", ProfileDetailView.as_view(), name="profile_detail")
else:
    profile_detail_default = url(r"^profile/(?P<username>[\w\._-]+)/$", ProfileDetailView.as_view(), name="profile_detail")


urlpatterns = patterns("idios.views",
    
    url(r"^$", ProfileListView.as_view(), name="profile_list"),
    url(r"^all/$", ProfileListView.as_view(all_profiles=True), name="profile_list_all"),
        
    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    url(r"^(?P<profile_slug>[\w\._-]+)/edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    
    url(r"^create/$", ProfileCreateView.as_view(), name="profile_create"),
    url(r"^(?P<profile_slug>[\w\._-]+)/create/$", ProfileCreateView.as_view(), name="profile_create"),
    
    profile_detail_default,
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<pk>\d+)/$", ProfileDetailView.as_view(), name="profile_detail"),
    
    url(r"^(?P<profile_slug>[\w\._-]+)/$", ProfileListView.as_view(), name="profile_list"),
)
