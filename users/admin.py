# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile

User = get_user_model()

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = 'user'
    fields = ('nickname', 'balance')
    extra = 0

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_username", "user_first_name", "user_last_name", "user_email", "nickname", "user_balance")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email", "nickname", "user__balance")

    def user_username(self, obj): return obj.user.username
    def user_first_name(self, obj): return obj.user.first_name
    def user_last_name(self, obj): return obj.user.last_name
    def user_email(self, obj): return obj.user.email
    def user_balance(self, obj): return obj.balance
