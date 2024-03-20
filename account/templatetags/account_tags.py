from django import template
from django.utils.html import conditional_escape
from django.utils.http import urlencode

from account.utils import user_display

register = template.Library()

class UserDisplayNode(template.Node):

    def __init__(self, user, as_var=None):
        self.user_var = template.Variable(user)
        self.as_var = as_var

    def render(self, context):
        try:
            user = self.user_var.resolve(context)
        except template.VariableDoesNotExist:
            return ""

        display = user_display(user) if user else "Unknown User"
        if self.as_var:
            context[self.as_var] = display
            return ""
        return conditional_escape(display)

@register.tag(name="user_display")
def do_user_display(parser, token):
    bits = token.split_contents()
    try:
        if len(bits) == 2:
            user = bits[1]
            as_var = None
        elif len(bits) == 4:
            user = bits[1]
            as_var = bits[3]
        else:
            raise template.TemplateSyntaxError(
                "'{0}' takes either two or four arguments".format(bits[0])
            )
    except ValueError:
        raise template.TemplateSyntaxError("Error in 'user_display' tag arguments")
    return UserDisplayNode(user, as_var)

class URLNextNode(URLNode):

    @staticmethod
    def add_next(url, context):
        redirect_field_name = context.get("redirect_field_name")
        redirect_field_value = context.get("redirect_field_value")
        if redirect_field_name and redirect_field_value:
            url += "?" + urlencode({redirect_field_name: redirect_field_value})
        return url

    def render(self, context):
        try:
            url = super(URLNextNode, self).render(context)
        except Exception as e:
            return f"Error rendering URL: {e}"

        if self.asvar:
            url = context[self.asvar]

        url = self.add_next(url, context)
        
        if self.asvar:
            context[self.asvar] = url
            return ""
        return url

@register.tag
def urlnext(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "'%s' takes at least one argument (path to a view)" % bits[0]
        )

    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None

    if len(bits) >= 2 and bits[-2] == "as":
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits[2:]:
        match = kwarg_re.match(bit)
        if not match:
            raise template.TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return URLNextNode(viewname, args, kwargs, asvar)
