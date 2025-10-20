from django import forms
from .models import Item
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
 
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
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
 
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
 
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
 
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
 
    class Meta:
        model = User
        fields = ['username', 'email']