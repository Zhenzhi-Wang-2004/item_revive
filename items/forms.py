from django import forms
from .models import Item
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
 
class ItemForm(forms.ModelForm): # 创建一个继承自forms.ModelForm的表单类，用于基于Item模型自动生成表单
    class Meta:
        model = Item # 指定这个表单基于Item模型
        fields = ['name', 'description', 'item_type', 'price', 'contact_info', 'image']
        labels = {
            'name': '物品名称',
            'description': '物品描述',
            'item_type': '交易类型',
            'price': '价格(出售时填写)',
            'contact_info': '联系方式',
            'image': '物品图片(可选)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].required = False

class UserRegisterForm(UserCreationForm): # 创建一个继承自UserCreationForm的表单类，用于用户注册
    email = forms.EmailField()
 
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
 
class UserUpdateForm(forms.ModelForm): # 创建一个继承自forms.ModelForm的表单类，用于更新用户信息
    email = forms.EmailField()
 
    class Meta:
        model = User
        fields = ['username', 'email']