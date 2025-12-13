"""ItemRevive 闲置物品共享平台 - 视图模块

本模块定义了系统的核心视图，包括用户认证、物品管理、个人资料管理等功能，
是连接前端界面和后端数据模型的桥梁。使用Django的函数视图和类视图两种方式实现，
支持用户认证、权限控制、动态表单处理和AJAX交互。

主要功能：
- 首页和物品列表展示
- 用户注册和登录
- 物品发布、编辑、删除和标记不可用
- 个人资料管理
- 动态属性字段加载（AJAX）
- 物品筛选和搜索

依赖：
- Django内置视图基类（ListView, DetailView, CreateView等）
- 自定义表单（DynamicItemForm, UserRegisterForm等）
- 数据模型（Item, ItemType, Profile）
- 用户认证和权限控制（LoginRequiredMixin, UserPassesTestMixin）
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from .models import Item, ItemType, Profile
from .forms import DynamicItemForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.db.models import Q
 
def home(request):
    """首页视图
    
    显示系统首页，包含6个最新的可用物品列表，按创建时间降序排列。
    
    参数:
        request: HTTP请求对象
    
    返回:
        HttpResponse: 渲染后的首页HTML响应
    """
    context = {
        'items': Item.objects.filter(is_available=True).order_by('-created_at')[:6]
    }
    return render(request, 'items/home.html', context)
 
class ItemListView(ListView):
    """物品列表视图
    
    显示可用物品的列表，支持分页、交易类型筛选、物品类别筛选和关键词搜索功能。
    继承自Django的ListView类视图，实现了自定义查询集和上下文数据。
    
    属性:
        model: 使用的模型类
        template_name: 渲染使用的模板
        context_object_name: 模板中使用的上下文变量名
        paginate_by: 每页显示的物品数量
    """
    model = Item
    template_name = 'items/item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        """获取筛选后的物品查询集
        
        根据URL参数对物品进行筛选和搜索：
        - 只显示可用物品（is_available=True）
        - 支持交易类型筛选（type参数：GIFT或SELL）
        - 支持物品类别筛选（category参数）
        - 支持关键词搜索（keyword参数，匹配名称和描述）
        
        返回:
            QuerySet: 筛选后的物品查询集
        """
        queryset = super().get_queryset().filter(is_available=True)
        
        # 交易类型筛选
        transaction_type = self.request.GET.get('type')
        if transaction_type in ['GIFT', 'SELL']:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # 物品类别筛选
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 关键词搜索
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(description__icontains=keyword)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """获取上下文数据
        
        添加所有可用的物品类别到上下文，用于筛选表单。
        
        参数:
            **kwargs: 父类传递的关键字参数
        
        返回:
            dict: 包含物品列表和物品类别的上下文数据
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = ItemType.objects.filter(is_active=True).order_by('name')
        return context
 
class UserItemListView(LoginRequiredMixin, ListView):
    """用户物品列表视图
    
    显示当前登录用户发布的所有物品，需要用户登录才能访问。
    继承自Django的ListView类视图，使用LoginRequiredMixin确保用户已认证。
    
    属性:
        model: 使用的模型类
        template_name: 渲染使用的模板
        context_object_name: 模板中使用的上下文变量名
        paginate_by: 每页显示的物品数量
    """
    model = Item
    template_name = 'items/user_item_list.html'
    context_object_name = 'items'
    paginate_by = 10
    
    def get_queryset(self):
        """获取当前用户的物品查询集
        
        筛选出当前登录用户发布的所有物品，按创建时间降序排列。
        
        返回:
            QuerySet: 当前用户的物品查询集
        """
        return Item.objects.filter(owner=self.request.user).order_by('-created_at')
 
class ItemDetailView(DetailView):
    """物品详情视图
    
    显示单个物品的详细信息，包括物品基本信息、动态属性、联系方式等。
    继承自Django的DetailView类视图。
    
    属性:
        model: 使用的模型类
        template_name: 渲染使用的模板
    """
    model = Item
    template_name = 'items/item_detail.html'

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """删除物品视图
    
    允许用户删除自己发布的物品，需要用户登录并拥有该物品的所有权。
    继承自Django的DeleteView类视图，使用LoginRequiredMixin确保用户已认证，
    使用UserPassesTestMixin确保用户有权限删除该物品。
    
    属性:
        model: 使用的模型类
        template_name: 渲染使用的模板
        success_url: 删除成功后的跳转URL
    """
    model = Item
    template_name = 'items/item_confirm_delete.html'
    success_url = '/my-items/'
    
    def test_func(self):
        """测试用户是否有权限删除物品
        
        检查当前登录用户是否是物品的所有者，如果是则允许删除。
        
        返回:
            bool: 用户是否有权限删除物品
        """
        item = self.get_object()
        return self.request.user == item.owner
 
def register(request):
    """用户注册视图
    
    处理用户注册请求，创建新用户和对应的用户资料，并设置默认的未批准状态。
    注册成功后，用户需要等待管理员批准才能使用完整功能。
    
    参数:
        request: HTTP请求对象
    
    返回:
        HttpResponse: 渲染后的注册页面HTML响应
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建用户资料并填充注册时提供的额外信息
            profile = Profile.objects.create(
                user=user,
                school=form.cleaned_data.get('school'),
                home_address=form.cleaned_data.get('home_address'),
                phone_number=form.cleaned_data.get('phone_number'),
                is_approved=False  # 默认未批准
            )
            username = form.cleaned_data.get('username')
            messages.success(request, f'账户 {username} 已创建，请等待管理员批准！')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'items/register.html', {'form': form})

class ItemCreateView(LoginRequiredMixin, CreateView):
    """物品创建视图
    
    允许已批准的用户发布新物品，支持动态属性字段的加载和表单处理。
    继承自Django的CreateView类视图，使用LoginRequiredMixin确保用户已认证，
    使用DynamicItemForm处理动态生成的物品属性字段。
    
    属性:
        model: 使用的模型类
        form_class: 表单类（使用动态表单）
        template_name: 渲染使用的模板
    """
    model = Item
    form_class = DynamicItemForm
    template_name = 'items/item_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """处理请求分发
        
        在处理请求前检查用户是否已被管理员批准，未批准用户无法发布物品。
        
        参数:
            request: HTTP请求对象
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            HttpResponse: 重定向或正常视图响应
        """
        if hasattr(request.user, 'profile') and not request.user.profile.is_approved:
            messages.error(request, '您的账户尚未被管理员批准，无法发布物品！')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """获取表单关键字参数
        
        准备表单所需的关键字参数，确保动态表单能正确接收POST数据。
        
        返回:
            dict: 表单关键字参数字典
        """
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs
    
    def post(self, request, *args, **kwargs):
        """处理POST请求
        
        区分两种POST请求：
        1. 加载属性字段的请求（action='load_attributes'）
        2. 正常的表单提交请求
        
        参数:
            request: HTTP请求对象
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            HttpResponse: 渲染后的表单页面或重定向响应
        """
        # 检查是否是加载属性的请求
        if request.POST.get('action') == 'load_attributes':
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            return self.render_to_response(self.get_context_data(form=form))
        # 否则，处理正常的表单提交
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """处理有效表单
        
        在保存表单前设置物品的所有者为当前登录用户。
        
        参数:
            form: 验证通过的表单实例
        
        返回:
            HttpResponse: 表单保存后的重定向响应
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """物品更新视图
    
    允许已批准的用户更新自己发布的物品信息，支持动态属性字段的加载和表单处理。
    继承自Django的UpdateView类视图，使用LoginRequiredMixin确保用户已认证，
    使用UserPassesTestMixin确保用户有权限更新该物品，使用DynamicItemForm处理动态生成的物品属性字段。
    
    属性:
        model: 使用的模型类
        form_class: 表单类（使用动态表单）
        template_name: 渲染使用的模板
    """
    model = Item
    form_class = DynamicItemForm  # 使用动态表单
    template_name = 'items/item_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """处理请求分发
        
        在处理请求前检查用户是否已被管理员批准，未批准用户无法更新物品。
        
        参数:
            request: HTTP请求对象
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            HttpResponse: 重定向或正常视图响应
        """
        if hasattr(request.user, 'profile') and not request.user.profile.is_approved:
            messages.error(request, '您的账户尚未被管理员批准，无法更新物品！')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """获取表单关键字参数
        
        准备表单所需的关键字参数，确保动态表单能正确接收POST数据以生成动态字段。
        
        返回:
            dict: 表单关键字参数字典
        """
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs
    
    def post(self, request, *args, **kwargs):
        """处理POST请求
        
        区分两种POST请求：
        1. 加载属性字段的请求（action='load_attributes'）
        2. 正常的表单提交请求
        
        参数:
            request: HTTP请求对象
            *args: 位置参数
            **kwargs: 关键字参数
        
        返回:
            HttpResponse: 渲染后的表单页面或重定向响应
        """
        if request.POST.get('action') == 'load_attributes':
            # 获取当前物品实例
            self.object = self.get_object()
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            # 渲染表单页面，显示动态属性字段
            return self.render_to_response(self.get_context_data(form=form))
        # 否则，处理正常的表单提交
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """处理有效表单
        
        在保存表单前设置物品的所有者为当前登录用户。
        
        参数:
            form: 验证通过的表单实例
        
        返回:
            HttpResponse: 表单保存后的重定向响应
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        """测试用户是否有权限更新物品
        
        检查当前登录用户是否是物品的所有者，如果是则允许更新。
        
        返回:
            bool: 用户是否有权限更新物品
        """
        item = self.get_object()
        return self.request.user == item.owner

@login_required
def profile(request):
    """个人资料管理视图
    
    允许登录用户更新自己的个人资料信息，包括用户基本信息和扩展资料。
    支持表单验证和成功消息提示。
    
    参数:
        request: HTTP请求对象
    
    返回:
        HttpResponse: 渲染后的个人资料页面HTML响应
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '您的资料已更新！')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'items/profile.html', context)
 
@login_required
def mark_unavailable(request, pk):
    """标记物品不可用视图
    
    允许物品所有者将自己发布的物品标记为不可用状态。
    
    参数:
        request: HTTP请求对象
        pk: 物品的主键ID
    
    返回:
        HttpResponseRedirect: 重定向到物品详情页面
    """
    item = get_object_or_404(Item, pk=pk)
    if request.user == item.owner:
        item.is_available = False
        item.save()
        messages.success(request, '物品已标记为不可用')
    return redirect('item-detail', pk=pk)

@login_required
def load_attributes(request):
    """AJAX视图函数，用于加载物品类型的动态属性字段
    
    通过AJAX请求加载指定物品类别的动态属性字段，支持创建和编辑两种场景。
    在编辑场景下，会检查用户是否有权限编辑该物品。
    
    参数:
        request: HTTP请求对象，包含以下POST参数：
            - category_id: 物品类别的ID
            - item_id: 物品的ID（可选，仅在编辑场景下提供）
    
    返回:
        JsonResponse: 包含以下内容的JSON响应：
            - 成功时：{'html': 动态属性字段的HTML代码}
            - 失败时：{'error': 错误信息}，并设置相应的HTTP状态码
                - 403: 无权限执行此操作
                - 400: 无效的请求方法
    """
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        item_id = request.POST.get('item_id')
        
        # 获取物品实例（如果是编辑操作）
        item_instance = None
        if item_id:
            item_instance = get_object_or_404(Item, pk=item_id)
            
            # 确保只有物品所有者可以编辑
            if request.user != item_instance.owner:
                return JsonResponse({'error': '没有权限执行此操作'}, status=403)
        
        # 创建表单实例并传递category_id
        form_kwargs = {
            'initial': {'category': category_id},
        }
        
        if item_instance:
            form_kwargs['instance'] = item_instance
        
        form = DynamicItemForm(**form_kwargs)
        
        # 渲染动态属性字段
        context = {'form': form}
        html = render(request, 'items/category_attributes.html', context).content.decode('utf-8')
        
        return JsonResponse({'html': html})
    
    return JsonResponse({'error': '无效的请求方法'}, status=400)