Below is an example of how to use a custom clean_password method which
harnesses the VeryFacistCheck from cracklib.

First add the path to the module which contains the
`AccountDefaultHookSet` subclass to your settings::

    ACCOUNT_HOOKSET = "scenemachine.hooks.AccountHookSet"

Then define the `clean_password` method::

    import cracklib

    from django import forms from django.conf import settings from
    django.template.defaultfilters import mark_safe from
    django.utils.translation import ugettext_lazy as _

    from account.hooks import AccountDefaultHookSet


    class AccountHookSet(AccountDefaultHookSet):

        def clean_password(self, password_new, password_new_confirm):
            password_new = super(AccountHookSet, self).clean_password(password_new, password_new_confirm)
            try:
                dictpath = "/usr/share/cracklib/pw_dict"
                if dictpath:
                    cracklib.VeryFascistCheck(password_new, dictpath=dictpath)
                else:
                    cracklib.VeryFascistCheck(password_new)
                return password_new
            except ValueError as e:
                message = _(unicode(e))
                raise forms.ValidationError, mark_safe(message)
            return password_new
