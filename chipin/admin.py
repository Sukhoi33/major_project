from django.contrib import admin
from .models import Group, Transaction


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "admin")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "created_at")
    search_fields = ("user__username", "amount", "created_at")
    list_filter = ("created_at",)