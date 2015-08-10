from __future__ import unicode_literals

from django import template
from django.template.base import kwarg_re
from django.template.defaulttags import URLNode
from django.utils.html import conditional_escape
from django.utils.http import urlencode

from account.utils import user_display


register = template.Library()


class UserDisplayNode(template.Node):

    def __init__(self, user, as_var=None):
        self.user_var = template.Variable(user)
        self.as_var = as_var

    def render(self, context):
        user = self.user_var.resolve(context)
        display = user_display(user)
        if self.as_var:
            context[self.as_var] = display
            return ""
        return conditional_escape(display)


@register.tag(name="user_display")
def do_user_display(parser, token):
    """
    Example usage::

        {% user_display user %}

    or if you need to use in a {% blocktrans %}::

        {% user_display user as user_display}
        {% blocktrans %}{{ user_display }} has sent you a gift.{% endblocktrans %}

    """
    bits = token.split_contents()
    if len(bits) == 2:
        user = bits[1]
        as_var = None
    elif len(bits) == 4:
        user = bits[1]
        as_var = bits[3]
    else:
        raise template.TemplateSyntaxError("'{0}' takes either two or four arguments".format(bits[0]))
    return UserDisplayNode(user, as_var)


class URLNextNode(URLNode):

    def add_next(self, url, context):
        """
        With both `redirect_field_name` and `redirect_field_value` available in
        the context, add on a querystring to handle "next" redirecting.
        """
        if all([key in context for key in ["redirect_field_name", "redirect_field_value"]]):
            if context["redirect_field_value"]:
                url += "?" + urlencode({
                    context["redirect_field_name"]: context["redirect_field_value"],
                })
        return url

    def render(self, context):
        url = super(URLNextNode, self).render(context)
        if self.asvar:
            url = context[self.asvar]
        # add on next handling
        url = self.add_next(url, context)
        if self.asvar:
            context[self.asvar] = url
            return ""
        else:
            return url


@register.tag
def urlnext(parser, token):
    """
    {% url %} copied from Django 1.7.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "'%s' takes at least one argument"
            " (path to a view)" % bits[0]
        )
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise template.TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return URLNextNode(viewname, args, kwargs, asvar)
