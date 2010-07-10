from django import template


register = template.Library()


@register.inclusion_tag("idios/profile_item.html")
def show_profile(user):
    return {"user": user}


@register.simple_tag
def clear_search_url(request):
    GET = request.GET.copy()
    if "search" in getvars:
        del GET["search"]
    if len(GET.keys()) > 0:
        return "%s?%s" % (request.path, GET.urlencode())
    else:
        return request.path
