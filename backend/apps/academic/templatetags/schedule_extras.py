from django import template

register = template.Library()


# @register.filter
# def get_item(dictionary, key):
#     return dictionary.get(key, [])

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return {}
    return dictionary.get(key, {})