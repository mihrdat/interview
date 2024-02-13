from django.db import transaction
from django.contrib import admin
from .models import DepositRequest, CreditTransactionLog


class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ["credit", "amount", "status", "created_at", "updated_at"]
    actions = ["approve_selected"]
    readonly_fields = ["credit", "amount", "created_at", "updated_at"]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == DepositRequest.STATUS_APPROVED:
            return self.readonly_fields + ["status"]
        return self.readonly_fields

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if obj.status == DepositRequest.STATUS_APPROVED:
            credit = obj.credit
            credit.balance += obj.amount
            credit.save(update_fields=["balance"])

            CreditTransactionLog.objects.create(
                credit=credit,
                amount=obj.amount,
                type=CreditTransactionLog.TYPE_DEPOSIT,
            )

        super().save_model(request, obj, form, change)


admin.site.register(DepositRequest, DepositRequestAdmin)
