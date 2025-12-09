from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    """用户扩展模型，添加额外的用户信息和审批状态"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    school = models.CharField(max_length=100, verbose_name="学校", blank=True)
    home_address = models.CharField(max_length=200, verbose_name="家庭地址", blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="联系电话", blank=True)
    is_approved = models.BooleanField(default=False, verbose_name="是否已批准")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.user.username} 的资料"

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

class ItemType(models.Model):
    """物品类型模型，存储类型名称及属性配置，如书籍、电子产品、食品"""
    name = models.CharField(max_length=100, verbose_name="类型名称")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "物品类型"
        verbose_name_plural = "物品类型"
        ordering = ['name']

class Attribute(models.Model):
    """属性字段模型，存储每个类型的必填属性，如作者、出版社"""
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
        return f"{self.item_type.name} - {self.name}"

    class Meta:
        verbose_name = "属性字段"
        verbose_name_plural = "属性字段"
        ordering = ['order']
        unique_together = ['item_type', 'name']

class Item(models.Model):
    """物品模型，关联动态属性"""
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
        return f"{self.name} ({self.get_transaction_type_display()})"

    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "物品"
        verbose_name_plural = "物品"
        ordering = ['-created_at']