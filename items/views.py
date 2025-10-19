from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Item
from .forms import ItemForm, UserRegisterForm, UserUpdateForm
 
def home(request):
    context = {
        'items': Item.objects.filter(is_available=True).order_by('-created_at')[:6]
    }
    return render(request, 'items/home.html', context)
 
class ItemListView(ListView):
    model = Item
    template_name = 'items/item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_available=True)
        item_type = self.request.GET.get('type')
        if item_type in ['GIFT', 'SELL']:
            queryset = queryset.filter(item_type=item_type)
        return queryset
 
class UserItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'items/user_item_list.html'
    context_object_name = 'items'
    paginate_by = 10
    
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user).order_by('-created_at')
 
class ItemDetailView(DetailView):
    model = Item
    template_name = 'items/item_detail.html'
 
class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'items/item_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
 
class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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
 
class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    template_name = 'items/item_confirm_delete.html'
    success_url = '/my-items/'
    
    def test_func(self):
        item = self.get_object()
        if self.request.user == item.owner:
            return True
        return False
 
def register(request):
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
def profile(request):
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
def mark_unavailable(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.user == item.owner:
        item.is_available = False
        item.save()
        messages.success(request, '物品已标记为不可用')
    return redirect('item-detail', pk=pk)