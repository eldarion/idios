from django.conf.urls.defaults import *
from idios.views import ProfilesListView


urlpatterns = patterns("idios.views",
    url(r"^$", ProfilesListView.as_view(), name="profile_list"),
    url(r"^edit/$", "profile_edit", name="profile_edit"),
    url(r"^create/$", "profile_create", name="profile_create"),
)
