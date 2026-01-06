from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Item, ItemType, Attribute, Profile

class AttributeInline(admin.TabularInline): # 以表格形式嵌入关联模型（Attribute）的编辑表单。
    """在物品类型编辑页嵌入属性编辑"""
    model = Attribute
    extra = 1
    ordering = ['order']

@admin.register(ItemType) # 注册 ItemType 模型到管理后台。
class ItemTypeAdmin(admin.ModelAdmin):
    """物品类型管理"""
    list_display = ('name', 'is_active', 'created_at', 'attribute_count') # 列表页显示的字段（名称、是否激活、创建时间、属性数量）。
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [AttributeInline] # 在 ItemType 编辑页嵌入 Attribute 的内联表单。
    
    def attribute_count(self, obj):
        return obj.attributes.count()
    attribute_count.short_description = "属性数量"

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """物品管理"""
    list_display = ('name', 'transaction_type', 'category', 'price', 
                   'owner', 'created_at', 'is_available') # 显示物品名称、交易类型、类别、价格、所有者、创建时间和可用状态。
    list_filter = ('transaction_type', 'category', 'is_available') # 按交易类型、类别、可用性过滤。
    search_fields = ('name', 'description', 'owner__username') # 支持按名称、描述、所有者用户名搜索。
    date_hierarchy = 'created_at' # 顶部显示按创建时间的日期导航。
    readonly_fields = ('dynamic_attributes',) # 将 dynamic_attributes 字段设为只读。

# 用户资料内联编辑
class ProfileInline(admin.StackedInline): # 以块形式嵌入关联模型（Profile）的编辑表单。
    model = Profile
    can_delete = False # 禁止删除内联的 Profile。
    verbose_name_plural = '用户资料' # 设置内联表单的标题。
    fields = ('school', 'home_address', 'phone_number', 'is_approved', 'created_at', 'updated_at') # 指定显示的字段（学校、地址、电话、是否批准、创建/更新时间）。
    readonly_fields = ('created_at', 'updated_at') # created_at 和 updated_at 为只读。

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
    
    def get_is_approved(self, obj): # 自定义方法，返回用户资料的 is_approved 状态。
        return obj.profile.is_approved if hasattr(obj, 'profile') else False
    get_is_approved.boolean = True
    get_is_approved.short_description = '已批准'

# 用户资料管理
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin): 
    list_display = ('user', 'school', 'phone_number', 'is_approved', 'created_at') # 显示关联用户、学校、电话、批准状态、创建时间。
    list_filter = ('is_approved',) # 按批准状态过滤。
    search_fields = ('user__username', 'school', 'phone_number') # 支持按用户名、学校、电话搜索。
    fields = ('user', 'school', 'home_address', 'phone_number', 'is_approved', 'created_at', 'updated_at')
    readonly_fields = ('user', 'created_at', 'updated_at')

# 替换默认 User 管理类
admin.site.unregister(User) # 取消注册 Django 默认的 User 管理类。
admin.site.register(User, CustomUserAdmin) # 注册自定义的 CustomUserAdmin，扩展用户管理功能。