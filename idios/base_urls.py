from django.conf.urls.defaults import *


urlpatterns = patterns("idios.views",
    url(r"^$", "profiles", name="profile_list"),
    url(r"^profile/(?P<username>[\w\._-]+)/$", "profile", name="profile_detail"),
    url(r"^edit/$", "profile_edit", name="profile_edit"),
    url(r"^create/$", "profile_create", name="profile_create"),
)
