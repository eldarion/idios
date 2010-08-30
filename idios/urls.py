from django.conf.urls.defaults import *

from idios.views import profiles, ALL_PROFILES

urlpatterns = patterns("",
    url(r"^all/$", profiles, {"profile_slug": ALL_PROFILES}, name="profile_list_all"),
    url(r"", include("idios.base_urls")),
    url(r"^(?P<profile_slug>[\w\._-]+)/", include("idios.base_urls")),
)
