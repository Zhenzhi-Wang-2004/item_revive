from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Item, ItemType, Attribute, Profile

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

# 用户资料内联编辑
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '用户资料'
    fields = ('school', 'home_address', 'phone_number', 'is_approved', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

# 用户管理
class ItemInline(admin.StackedInline):
    model = Item
    can_delete = False
    verbose_name_plural = '物品'
    extra = 0

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, ItemInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_is_approved')
    list_filter = ('is_staff', 'is_active', 'profile__is_approved')
    
    def get_is_approved(self, obj):
        return obj.profile.is_approved if hasattr(obj, 'profile') else False
    get_is_approved.boolean = True
    get_is_approved.short_description = '已批准'

# 用户资料管理
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'phone_number', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'school', 'phone_number')
    fields = ('user', 'school', 'home_address', 'phone_number', 'is_approved', 'created_at', 'updated_at')
    readonly_fields = ('user', 'created_at', 'updated_at')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)