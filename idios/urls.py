from django.conf.urls.defaults import *

from idios.views import ProfilesListView


urlpatterns = patterns("idios.views",
    url(r"^profile/(?P<username>[\w\._-]+)/$", "profile", name="profile_detail"),
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<profile_pk>\d+)/$", "profile_by_pk", name="profile_detail"),
    url(r"^all/$", ProfilesListView.as_view(all_profiles=True), 
            name="profile_list_all"),
    url(r"", include("idios.urls_base")),
    url(r"^(?P<profile_slug>[\w\._-]+)/", include("idios.urls_base")),
)
