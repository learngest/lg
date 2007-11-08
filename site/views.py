# -*- encoding: utf-8 -*-
# vim:encoding=utf-8:

from django.conf import settings
from django.http import Http404
from django.views.generic.list_detail import object_detail

from pages.models import Page

def page_detail(request, section, slug=None):
    pages = Page.objects.filter(section=section)
    if not slug:
        try:
            slug = pages.latest('date').slug
        except Page.DoesNotExist:
            raise Http404(u'No page found in section "%s".' % section)
    pages_list = pages.filter(section=section)
    return object_detail(request,
                queryset = pages,
                slug = slug,
                slug_field = 'slug',
                extra_context = {'pages_list': pages_list,}
                )

