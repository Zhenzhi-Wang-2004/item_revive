from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.urls import reverse
 
class Item(models.Model):
    ITEM_TYPE_CHOICES = [
        ('GIFT', '赠送'),
        ('SELL', '出售'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="物品名称")
    description = models.TextField(verbose_name="物品描述")
    item_type = models.CharField(max_length=4, choices=ITEM_TYPE_CHOICES, verbose_name="交易类型")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="价格(出售时填写)")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所有者")
    contact_info = models.CharField(max_length=200, verbose_name="联系方式")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    image = models.ImageField(upload_to='item_images/', blank=True, null=True, verbose_name="物品图片")
    is_available = models.BooleanField(default=True, verbose_name="是否可用")
 
    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"
 
    def get_absolute_url(self):
        return reverse('item-detail', kwargs={'pk': self.pk})
 
    class Meta:
        verbose_name = "物品"
        verbose_name_plural = "物品"
        ordering = ['-created_at']