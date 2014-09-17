from __future__ import unicode_literals

from django import forms
from account.conf import settings
from django.template import Context
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


def account_delete_mark(deletion):
    deletion.user.is_active = False
    deletion.user.save()


def account_delete_expunge(deletion):
    deletion.user.delete()


def clean_password(password_new, password_new_confirm):
    if password_new != password_new_confirm:
        raise forms.ValidationError(_("You must type the same password each time."))
    return password_new


def clean_password_cracklib(password_new, password_new_confirm):
    import cracklib

    password_new = clean_password(password_new, password_new_confirm)

    try:
        dictpath = settings.ACCOUNT_CRACKLIB_DICTPATH
        if dictpath:
            cracklib.VeryFascistCheck(password_new, dictpath=dictpath)
        else:
            cracklib.VeryFascistCheck(password_new)
        return password_new
    except ValueError as e:
        message = _(unicode(e))
        error_template = settings.ACCOUNT_CRACKLIB_ERROR_TEMPLATE
        if error_template:
            template = loader.get_template(error_template)
            output = template.render(Context({"message": message}))
        else:
            output = message
        raise forms.ValidationError, mark_safe(output)
    return password_new
