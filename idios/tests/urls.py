from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^profiles/", include("idios.urls"))
)