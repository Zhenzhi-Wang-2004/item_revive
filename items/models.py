from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.urls import reverse

# 定义物品模型类
class Item(models.Model):
    # 每个元组包含两个元素：
    # 1. 存储在数据库中的值（字符串）
    # 2. 显示在表单/后台的可读名称
    ITEM_TYPE_CHOICES = [
        ('GIFT', '赠送'),
        ('SELL', '出售'),
    ]
    name = models.CharField(max_length=100, verbose_name="物品名称") # CharField: 字符串字段 verbose_name: 在后台显示的字段名称
    description = models.TextField(verbose_name="物品描述") # TextField: 长文本字段
    item_type = models.CharField(max_length=4, choices=ITEM_TYPE_CHOICES, verbose_name="交易类型") # choices: 使用上面定义的 ITEM_TYPE_CHOICES 作为选项
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="价格(出售时填写)") 
    # DecimalField: 十进制数字段 max_digits: 总位数 decimal_places: 小数位数 blank=True, null=True: 允许在表单中为空且数据库中可为NULL
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者") # ForeignKey: 外键关系，关联到Django内置的User模型
    # on_delete=models.CASCADE: 当关联的用户被删除时，同时删除该用户的所有物品
    contact_info = models.CharField(max_length=200, verbose_name="联系方式")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    # DateTimeField: 日期时间字段 auto_now_add=True: 对象首次创建时自动设置为当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间") # auto_now=True: 每次保存对象时自动更新为当前时间
    image = models.ImageField(upload_to='item_images/', blank=True, null=True, verbose_name="物品图片") # ImageField: 图片上传字段 # upload_to: 指定上传图片的保存路径
    is_available = models.BooleanField(default=True, verbose_name="是否可用") # BooleanField: 布尔值字段
 
    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"
 
    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'pk': self.pk})
 
    class Meta:
        verbose_name = "物品"
        verbose_name_plural = "物品"
        ordering = ['-created_at']