"""ItemRevive 闲置物品共享平台 - 数据模型模块

本模块定义了系统的核心数据模型，包括用户资料、物品类型、属性字段和物品信息等，
是整个系统的数据基础。所有模型均继承自 Django 的 models.Model 类，使用 Django ORM 
进行数据库操作。

主要功能：
- 用户扩展信息管理（Profile）
- 灵活的物品类型定义（ItemType）
- 动态属性字段配置（Attribute）
- 物品信息存储与动态属性关联（Item）

数据关系：
- User 与 Profile 为一对一关系
- ItemType 与 Attribute 为一对多关系
- ItemType 与 Item 为一对多关系
- User 与 Item 为一对多关系
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    """用户扩展模型
    
    扩展Django内置的User模型，存储额外的用户信息和账户审批状态。
    实现了新用户注册后的审批机制，只有管理员批准的用户才能使用完整功能。
    
    属性:
        user: 与Django内置User模型的一对一关系
        school: 用户所在学校
        home_address: 用户家庭地址
        phone_number: 用户联系电话
        is_approved: 用户账户是否已被管理员批准
        created_at: 资料创建时间
        updated_at: 资料最后更新时间
    
    方法:
        __str__: 返回用户资料的字符串表示
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    school = models.CharField(max_length=100, verbose_name="学校", blank=True)
    home_address = models.CharField(max_length=200, verbose_name="家庭地址", blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="联系电话", blank=True)
    is_approved = models.BooleanField(default=False, verbose_name="是否已批准")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        """返回用户资料的字符串表示"""
        return f"{self.user.username} 的资料"

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

class ItemType(models.Model):
    """物品类型模型
    
    定义物品的分类，每个类型可以配置独特的属性字段（通过Attribute模型关联）。
    支持启用/禁用特定类型，只有启用的类型才能在前端被用户选择使用。
    
    属性:
        name: 物品类型名称（如"书籍"、"电子产品"、"食品"）
        is_active: 类型是否启用
        created_at: 类型创建时间
        attributes: 与Attribute模型的一对多关系，通过related_name访问
    
    方法:
        __str__: 返回物品类型的字符串表示
    
    元数据:
        按名称升序排列
        提供友好的复数名称
    """
    name = models.CharField(max_length=100, verbose_name="类型名称")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        """返回物品类型的字符串表示"""
        return self.name

    class Meta:
        verbose_name = "物品类型"
        verbose_name_plural = "物品类型"
        ordering = ['name']

class Attribute(models.Model):
    """属性字段模型
    
    定义每种物品类型的动态属性字段，支持多种字段类型和配置选项。
    与ItemType模型建立一对多关系，实现了灵活的物品属性管理系统。
    
    常量:
        TYPE_CHOICES: 支持的字段类型选项列表
            - char: 短文本字段
            - text: 长文本字段
            - number: 数字字段
            - date: 日期字段
    
    属性:
        item_type: 所属的物品类型（外键关系）
        name: 属性名称（如"作者"、"出版社"、"品牌"）
        field_type: 字段类型（从TYPE_CHOICES中选择）
        is_required: 该属性是否为必填项
        order: 属性在表单中的显示顺序
    
    方法:
        __str__: 返回属性字段的字符串表示
    
    元数据:
        按order字段升序排列
        确保在同一物品类型下属性名称唯一
        提供友好的复数名称
    """
    TYPE_CHOICES = [
        ('char', '文本'),
        ('text', '长文本'),
        ('number', '数字'),
        ('date', '日期'),
    ]
    
    item_type = models.ForeignKey(ItemType, related_name='attributes', on_delete=models.CASCADE, verbose_name="所属类型")
    name = models.CharField(max_length=100, verbose_name="属性名称")
    field_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="字段类型")
    is_required = models.BooleanField(default=True, verbose_name="是否必填")
    order = models.PositiveIntegerField(default=0, verbose_name="显示顺序")

    def __str__(self):
        """返回属性字段的字符串表示"""
        return f"{self.item_type.name} - {self.name}"

    class Meta:
        verbose_name = "属性字段"
        verbose_name_plural = "属性字段"
        ordering = ['order']
        unique_together = ['item_type', 'name']

class Item(models.Model):
    """物品模型
    
    定义闲置物品的核心信息，支持动态属性存储和多种交易类型。
    与User模型（所有者）和ItemType模型（分类）建立关联，使用JSONField
    存储与物品类型相关的动态属性。
    
    常量:
        ITEM_TYPE_CHOICES: 支持的交易类型选项列表
            - GIFT: 赠送
            - SELL: 出售
    
    属性:
        name: 物品名称
        description: 物品详细描述
        transaction_type: 交易类型（从ITEM_TYPE_CHOICES中选择）
        price: 价格（仅出售时填写，可为空）
        owner: 物品所有者（外键关系）
        contact_email: 联系人邮箱
        contact_phone: 联系人手机
        category: 物品所属类型（外键关系）
        dynamic_attributes: 动态属性存储（JSON格式，与物品类型的Attribute关联）
        created_at: 物品发布时间
        updated_at: 物品信息最后更新时间
        image: 物品图片（可选）
        is_available: 物品是否可用（默认为True）
    
    方法:
        __str__: 返回物品的字符串表示，包含名称和交易类型
        get_absolute_url: 获取物品详情页面的绝对URL
    
    元数据:
        按发布时间倒序排列
        提供友好的复数名称
    """
    ITEM_TYPE_CHOICES = [
        ('GIFT', '赠送'),
        ('SELL', '出售'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="物品名称")
    description = models.TextField(verbose_name="物品描述")
    transaction_type = models.CharField(max_length=4, choices=ITEM_TYPE_CHOICES, verbose_name="交易类型")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="价格(出售时填写)")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")
    contact_email = models.EmailField(verbose_name='联系人邮箱')
    contact_phone = models.CharField(max_length=20, verbose_name='联系人手机')
    category = models.ForeignKey(ItemType, on_delete=models.SET_NULL, null=True, verbose_name="物品类型")
    dynamic_attributes = models.JSONField(default=dict, blank=True, verbose_name="动态属性")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    image = models.ImageField(upload_to='item_images/', blank=True, null=True, verbose_name="物品图片")
    is_available = models.BooleanField(default=True, verbose_name="是否可用")

    def __str__(self):
        """返回物品的字符串表示"""
        return f"{self.name} ({self.get_transaction_type_display()})"

    def get_absolute_url(self):
        """获取物品详情页面的绝对URL
        
        返回物品详情页面的URL路径，用于Django的reverse函数生成完整URL。
        
        返回:
            str: 物品详情页面的URL路径
        """
        return reverse('item-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "物品"
        verbose_name_plural = "物品"
        ordering = ['-created_at']