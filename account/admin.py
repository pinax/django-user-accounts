from __future__ import unicode_literals

from django.contrib import admin

from account.models import Account, SignupCode, AccountDeletion, EmailAddress


class SignupCodeAdmin(admin.ModelAdmin):

    list_display = ["code", "max_uses", "use_count", "expiry", "created"]
    search_fields = ["code", "email"]
    list_filter = ["created"]
    raw_id_fields = ["inviter"]


class AccountAdmin(admin.ModelAdmin):

    raw_id_fields = ["user"]


class AccountDeletionAdmin(AccountAdmin):

    list_display = ["email", "date_requested", "date_expunged"]


class EmailAddressAdmin(AccountAdmin):

    list_display = ["user", "email", "verified", "primary"]
    search_fields = ["email", "user__username"]
    list_filter = ["user"]


admin.site.register(Account, AccountAdmin)
admin.site.register(SignupCode, SignupCodeAdmin)
admin.site.register(AccountDeletion, AccountDeletionAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
