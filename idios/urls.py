from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^$", "idios.views.profiles", name="profile_list"),
    url(r"^profile/(?P<username>[\w\._-]+)/$", "idios.views.profile", name="profile_detail"),
    url(r"^edit/$", "idios.views.profile_edit", name="profile_edit"),
)
