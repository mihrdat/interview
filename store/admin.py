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
    def approve_selected(self, request, queryset):
        for deposit_request in queryset:
            if deposit_request.status == DepositRequest.STATUS_PENDING:
                deposit_request.status = DepositRequest.STATUS_APPROVED
                deposit_request.save(update_fields=["status"])

                credit = deposit_request.credit
                credit.balance += deposit_request.amount
                credit.save(update_fields=["balance"])

                CreditTransactionLog.objects.create(
                    credit=credit,
                    amount=deposit_request.amount,
                    type=CreditTransactionLog.TYPE_DEPOSIT,
                )


admin.site.register(DepositRequest, DepositRequestAdmin)
