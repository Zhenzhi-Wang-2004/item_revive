from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Item
from .forms import ItemForm, UserRegisterForm, UserUpdateForm
 
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
        item_type = self.request.GET.get('type')
        if item_type in ['GIFT', 'SELL']: # 支持通过URL参数type过滤物品类型(GIFT或SELL)
            queryset = queryset.filter(item_type=item_type)
        return queryset
 
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
 
class ItemCreateView(LoginRequiredMixin, CreateView): # 创建物品视图 (类视图)
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
 
class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): # 更新物品视图 (类视图)
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        item = self.get_object()
        if self.request.user == item.owner:
            return True
        return False
 
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