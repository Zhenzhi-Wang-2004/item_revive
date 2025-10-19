from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Item
 
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'price', 'owner', 'created_at', 'is_available')
    list_filter = ('item_type', 'is_available')
    search_fields = ('name', 'description', 'owner__username')
    date_hierarchy = 'created_at'
 
admin.site.register(Item, ItemAdmin)
 
# 将用户资料添加到用户管理界面
class UserProfileInline(admin.StackedInline):
    model = Item
    can_delete = False
    verbose_name_plural = '物品'
 
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
 
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)