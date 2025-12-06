from django import forms
from .models import Item, ItemType, Attribute
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DynamicItemForm(forms.ModelForm):
    """动态生成物品表单，根据选择的类型显示对应属性"""
    class Meta:
        model = Item
        fields = ['name', 'description', 'transaction_type', 'price', 
                 'contact_email', 'contact_phone', 'category', 'image']
        labels = {
            'name': '物品名称',
            'description': '物品描述',
            'transaction_type': '交易类型',
            'price': '价格(出售时填写)',
            'contact_email': '联系人邮箱',
            'contact_phone': '联系人手机',
            'category': '物品类型',
            'image': '物品图片(可选)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].required = False
        
        # 动态添加属性字段
        category_id = self.data.get('category') or (self.instance.category.id if self.instance and self.instance.category else None)
        if category_id:
            try:
                item_type = ItemType.objects.get(id=category_id)
                for attr in item_type.attributes.order_by('order'):
                    field_kwargs = {
                        'label': attr.name,
                        'required': attr.is_required,
                        'widget': forms.TextInput()
                    }
                    
                    # 根据字段类型设置不同控件
                    if attr.field_type == 'text':
                        field_kwargs['widget'] = forms.Textarea(attrs={'rows': 3})
                    elif attr.field_type == 'number':
                        field_kwargs['widget'] = forms.NumberInput()
                    elif attr.field_type == 'date':
                        field_kwargs['widget'] = forms.DateInput(attrs={'type': 'date'})
                    
                    # 设置初始值
                    if self.instance and self.instance.dynamic_attributes:
                        field_kwargs['initial'] = self.instance.dynamic_attributes.get(attr.name)
                    
                    self.fields[f'attr_{attr.id}'] = forms.CharField(** field_kwargs)
            except ItemType.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        
        # 收集动态属性值
        dynamic_attrs = {}
        if category:
            for attr in category.attributes.all():
                attr_value = cleaned_data.get(f'attr_{attr.id}')
                if attr.is_required and not attr_value:
                    self.add_error(f'attr_{attr.id}', f'{attr.name}为必填项')
                dynamic_attrs[attr.name] = attr_value
        
        cleaned_data['dynamic_attributes'] = dynamic_attrs
        return cleaned_data

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