from django.conf.urls.defaults import *

from idios.views import ALL_PROFILES


urlpatterns = patterns("idios.views",
    url(r"^all/$", "profiles", {"profile_slug": ALL_PROFILES}, name="profile_list_all"),
    url(r"^profile/(?P<username>[\w\._-]+)/$", "profile", name="profile_detail"),
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<profile_pk>\d+)/$", "profile_by_pk", name="profile_detail"),
    url(r"", include("idios.urls_base")),
    url(r"^(?P<profile_slug>[\w\._-]+)/", include("idios.urls_base")),
)
