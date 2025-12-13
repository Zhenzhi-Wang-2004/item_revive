"""ItemRevive 闲置物品共享平台 - 表单模块

本模块定义了系统中使用的各种表单，包括物品发布表单、用户注册表单和个人资料更新表单等。
这些表单是用户与系统交互的重要界面元素，负责数据的收集、验证和处理。

主要表单类：
- DynamicItemForm: 动态物品表单，根据选择的物品类型显示对应属性
- UserRegisterForm: 用户注册表单，扩展了Django默认的用户创建表单
- UserUpdateForm: 用户信息更新表单
- ProfileUpdateForm: 个人资料更新表单

依赖：
- Django内置表单类（forms.ModelForm, UserCreationForm）
- 自定义数据模型（Item, ItemType, Profile）
- Django用户模型（User）
"""
from django import forms
from .models import Item, ItemType, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DynamicItemForm(forms.ModelForm):
    """动态物品表单
    
    一个智能表单，根据用户选择的物品类型动态生成对应的属性字段。
    继承自Django的ModelForm类，实现了动态字段生成、字段类型适配和属性值验证等功能。
    
    主要功能：
    - 根据选择的物品类型动态添加对应的属性字段
    - 根据属性类型自动选择合适的表单控件（文本框、数字框、日期选择器等）
    - 处理物品的基本信息和动态属性的收集与验证
    - 支持物品的创建和编辑两种场景
    
    内部类：
    - Meta: 定义表单的元数据，包括使用的模型、字段、标签和小部件
    """
    class Meta:
        model = Item
        fields = ['name', 'description', 'transaction_type', 'price', 
                 'contact_email', 'contact_phone', 'category', 'image', 'dynamic_attributes']
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
        widgets = {
            'dynamic_attributes': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """初始化表单实例
        
        设置表单的基本配置，并根据选择的物品类型动态生成属性字段。
        
        参数:
            *args: 位置参数，传递给父类构造函数
            **kwargs: 关键字参数，传递给父类构造函数
        """
        super().__init__(*args, **kwargs)
        # 设置价格字段为非必填，因为赠送物品不需要填写价格
        self.fields['price'].required = False
        
        # 动态添加属性字段的逻辑
        category_id = None
        # 1. 优先从POST数据中获取category_id（用户选择的新类型）
        if self.data:
            category_id = self.data.get('category')
        # 2. 如果没有POST数据，尝试从实例中获取（编辑已有物品时）
        if not category_id and self.instance and self.instance.category:
            category_id = self.instance.category.id
        # 3. 如果仍没有，尝试从初始数据中获取
        if not category_id and self.initial:
            category_id = self.initial.get('category')
        
        if category_id:
            try:
                # 确保category_id是整数类型
                category_id = int(category_id)
                # 获取对应的物品类型实例
                item_type = ItemType.objects.get(id=category_id)
                # 遍历该物品类型的所有属性，按order字段排序
                for attr in item_type.attributes.order_by('order'):
                    # 基本字段配置
                    field_kwargs = {
                        'label': attr.name,
                        'required': attr.is_required,
                        'widget': forms.TextInput()  # 默认使用文本输入框
                    }
                    
                    # 根据属性类型选择合适的表单控件
                    if attr.field_type == 'text':
                        # 文本类型使用多行文本框
                        field_kwargs['widget'] = forms.Textarea(attrs={'rows': 3})
                    elif attr.field_type == 'number':
                        # 数字类型使用数字输入框
                        field_kwargs['widget'] = forms.NumberInput()
                    elif attr.field_type == 'date':
                        # 日期类型使用日期选择器
                        field_kwargs['widget'] = forms.DateInput(attrs={'type': 'date'})
                    
                    # 如果是编辑已有物品，设置属性的初始值
                    if self.instance and self.instance.dynamic_attributes:
                        field_kwargs['initial'] = self.instance.dynamic_attributes.get(attr.name)
                    
                    # 将动态字段添加到表单中，字段名为"attr_" + 属性ID
                    self.fields[f'attr_{attr.id}'] = forms.CharField(**field_kwargs)
            except ItemType.DoesNotExist:
                # 如果物品类型不存在，忽略并继续执行
                pass

    def clean(self):
        """表单数据清洗和验证方法
        
        重写父类的clean方法，用于处理和验证表单数据，特别是收集动态属性值并进行验证。
        
        返回:
            dict: 清洗后的表单数据，包含基本字段和动态属性字段
                - dynamic_attributes: 字典类型，包含所有动态属性的名称和值
        """
        # 调用父类的clean方法获取基本字段的清洗数据
        cleaned_data = super().clean()
        # 获取选择的物品类别
        category = cleaned_data.get('category')
        
        # 收集动态属性值的字典
        dynamic_attrs = {}
        
        if category:
            # 遍历该物品类别的所有属性
            for attr in category.attributes.all():
                # 获取表单中对应属性的值
                attr_value = cleaned_data.get(f'attr_{attr.id}')
                # 验证必填属性
                if attr.is_required and not attr_value:
                    # 添加错误信息
                    self.add_error(f'attr_{attr.id}', f'{attr.name}为必填项')
                # 将属性值添加到字典中
                dynamic_attrs[attr.name] = attr_value
        
        # 将动态属性字典添加到清洗后的数据中
        cleaned_data['dynamic_attributes'] = dynamic_attrs
        # 返回清洗后的数据
        return cleaned_data

class UserRegisterForm(UserCreationForm):
    """用户注册表单
    
    扩展了Django内置的UserCreationForm，用于用户注册时收集更详细的信息。
    除了默认的用户名、密码字段外，还添加了邮箱、学校、家庭地址和联系电话等字段。
    
    额外添加的字段：
    - email: 用户邮箱，必填字段
    - school: 用户所在学校，必填字段
    - home_address: 用户家庭地址，必填字段
    - phone_number: 用户联系电话，必填字段
    
    内部类：
    - Meta: 定义表单的元数据，包括使用的模型和字段
    """
    email = forms.EmailField(required=True)
    school = forms.CharField(max_length=100, required=True, label='学校')
    home_address = forms.CharField(max_length=200, required=True, label='家庭地址')
    phone_number = forms.CharField(max_length=20, required=True, label='联系电话')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    """用户信息更新表单
    
    用于更新用户的基本信息，继承自Django的ModelForm类。
    主要用于用户个人资料页面中更新用户名和邮箱信息。
    
    字段：
    - username: 用户名
    - email: 用户邮箱
    
    内部类：
    - Meta: 定义表单的元数据，包括使用的模型和字段
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    """个人资料更新表单
    
    用于更新用户的扩展资料信息，继承自Django的ModelForm类。
    主要用于用户个人资料页面中更新学校、家庭地址和联系电话等扩展信息。
    
    字段：
    - school: 用户所在学校
    - home_address: 用户家庭地址
    - phone_number: 用户联系电话
    
    内部类：
    - Meta: 定义表单的元数据，包括使用的模型和字段
    """
    class Meta:
        model = Profile
        fields = ['school', 'home_address', 'phone_number']