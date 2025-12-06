from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Item, ItemType, Attribute

class AttributeInline(admin.TabularInline):
    """在物品类型编辑页嵌入属性编辑"""
    model = Attribute
    extra = 1
    ordering = ['order']

@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    """物品类型管理"""
    list_display = ('name', 'is_active', 'created_at', 'attribute_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [AttributeInline]
    
    def attribute_count(self, obj):
        return obj.attributes.count()
    attribute_count.short_description = "属性数量"

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """物品管理"""
    list_display = ('name', 'transaction_type', 'category', 'price', 
                   'owner', 'created_at', 'is_available')
    list_filter = ('transaction_type', 'category', 'is_available')
    search_fields = ('name', 'description', 'owner__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('dynamic_attributes',)

# 用户管理
class UserProfileInline(admin.StackedInline):
    model = Item
    can_delete = False
    verbose_name_plural = '物品'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)