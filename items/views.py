from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from .models import Item, ItemType
from .forms import DynamicItemForm, UserRegisterForm, UserUpdateForm
from django.db.models import Q
 
def home(request): # 首页视图 (函数视图)
    context = {
        'items': Item.objects.filter(is_available=True).order_by('-created_at')[:6]
    } # 显示6个最新的可用物品，按创建时间降序排列，只显示is_available=True的物品
    return render(request, 'items/home.html', context) # 使用home.html模板渲染
 
class ItemListView(ListView): # 物品列表视图 (类视图)，继承ListView显示物品列表
    model = Item
    template_name = 'items/item_list.html' # 使用item_list.html模板
    context_object_name = 'items'
    paginate_by = 12 # 每页显示12个物品
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_available=True) # 只显示可用物品
        
        # 交易类型筛选
        transaction_type = self.request.GET.get('type')
        if transaction_type in ['GIFT', 'SELL']: # 支持通过URL参数type过滤交易类型(GIFT或SELL)
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
        context = super().get_context_data(**kwargs)
        # 添加所有可用的物品类别到上下文
        context['categories'] = ItemType.objects.filter(is_active=True).order_by('name')
        return context
 
class UserItemListView(LoginRequiredMixin, ListView): # 用户物品列表视图 (类视图)，需要登录才能访问(LoginRequiredMixin)
    model = Item
    template_name = 'items/user_item_list.html'
    context_object_name = 'items'
    paginate_by = 10 # 每页显示10个物品
    
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user).order_by('-created_at') # 显示当前用户的所有物品，按创建时间降序排列
 
class ItemDetailView(DetailView): # 物品详情视图 (类视图)
    model = Item
    template_name = 'items/item_detail.html'

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): # 删除物品视图 (类视图)
    model = Item
    template_name = 'items/item_confirm_delete.html'
    success_url = '/my-items/'
    
    def test_func(self):
        item = self.get_object()
        if self.request.user == item.owner:
            return True
        return False
 
def register(request): # 用户注册视图 (函数视图)
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'账户 {username} 已创建，请登录！')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'items/register.html', {'form': form})

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = DynamicItemForm  # 使用动态表单
    template_name = 'items/item_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 确保表单能正确接收 POST 数据以生成动态字段
        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs
    
    def post(self, request, *args, **kwargs):
        # 检查是否是加载属性的请求
        if request.POST.get('action') == 'load_attributes':
            # 创建表单实例并传递POST数据，用于生成动态字段
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            # 渲染表单页面，显示动态属性字段
            return self.render_to_response(self.get_context_data(form=form))
        # 否则，处理正常的表单提交
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    form_class = DynamicItemForm  # 使用动态表单
    template_name = 'items/item_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 确保表单能正确接收 POST 数据以生成动态字段
        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs
    
    def post(self, request, *args, **kwargs):
        # 检查是否是加载属性的请求
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
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        item = self.get_object()
        return self.request.user == item.owner

@login_required
def profile(request): # 用户资料视图 (函数视图)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'您的账户信息已更新')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
    
    context = {
        'u_form': u_form
    }
    return render(request, 'items/profile.html', context)
 
@login_required
def mark_unavailable(request, pk): # 标记物品不可用视图 (函数视图)
    item = get_object_or_404(Item, pk=pk)
    if request.user == item.owner:
        item.is_available = False
        item.save()
        messages.success(request, '物品已标记为不可用')
    return redirect('item-detail', pk=pk)

@login_required
def load_attributes(request):
    """AJAX视图函数，用于加载物品类型的动态属性字段"""
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