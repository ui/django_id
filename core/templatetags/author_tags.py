import re

from django import template
from django.contrib.auth.models import User

register = template.Library()

class TopAuthors(template.Node):
    def __init__(self, limit, var_name):
        self.limit = int(limit)
        self.var_name = var_name

    def render(self, context):
        users = User.objects.raw("select *, count(auth_user.id) as total from auth_user join blog_posts on blog_posts.author_id = auth_user.id group by auth_user.id order by total desc")
        context[self.var_name] = users
        return ''

@register.tag
def get_top_authors(parser, token):
    """
    Gets any number of top authors and stores them in a varable.

    Syntax::

        {% get_top_authors [limit] as [var_name] %}

    Example usage::

        {% get_top_authors 10 as latest_post_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return TopAuthors(format_string, var_name)