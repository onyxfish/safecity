from urllib import quote_plus
from urlparse import urljoin

from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def build_media_url(uri):
    """
    Take a bit of url (uri) and put it together with the media url
    urljoin doesn't work like you think it would work. It likes to
    throw bits of the url away unless things are just right.
    """
    uri = "/".join(map(quote_plus,uri.split("/")))
    if getattr(settings, 'MEDIA_URL', False):
        if uri.startswith('/'):
            return urljoin(settings.MEDIA_URL, uri[1:])
        else:
            return urljoin(settings.MEDIA_URL, uri)
    else:
        return uri