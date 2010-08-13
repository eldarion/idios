from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^(?P<profile_slug>[\w\._-]+)/$", "idios.views.profiles", name="profile_list"),
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<username>[\w\._-]+)/$", "idios.views.profile", name="profile_detail"),
    url(r"^(?P<profile_slug>[\w\._-]+)/edit/$", "idios.views.profile_edit", name="profile_edit"),
    url(r"^(?P<profile_slug>[\w\._-]+)/create/$", "idios.views.profile_create", name="profile_create"),
)
