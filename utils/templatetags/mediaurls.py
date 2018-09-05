from mediagenerator import utils
from django import template

register = template.Library()

@register.simple_tag
def media_urls(name):
    return ','.join(['"' + url + '"' for url in utils.media_urls(name)])                                                                