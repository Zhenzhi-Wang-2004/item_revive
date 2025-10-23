# 定义了 Django 应用的 URL 路由配置，将 URL 模式映射到相应的视图函数或类视图

from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    home,
    ItemListView,
    UserItemListView,
    ItemDetailView,
    ItemCreateView,
    ItemUpdateView,
    ItemDeleteView,
    register,
    profile,
    mark_unavailable
)
 
urlpatterns = [
    path('', home, name='home'), # 根 URL ('') 映射到 home 视图函数
    path('items/', ItemListView.as_view(), name='item-list'), # '/items/' URL 映射到 ItemListView 类视图
    path('my-items/', UserItemListView.as_view(), name='user-item-list'), # '/my-items/' URL 映射到 UserItemListView 类视图

    # '/item/int:pk/' 动态 URL，其中 <int:pk> 捕获整数作为主键参数，映射到 ItemDetailView 类视图
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item-detail'), 
    # '/item/new/' URL 映射到 ItemCreateView 类视图，用于创建新物品的表单
    path('item/new/', ItemCreateView.as_view(), name='item-create'), 
    # '/item/int:pk/update/' 动态 URL，捕获物品 ID，映射到 ItemUpdateView 类视图，用于更新指定物品
    path('item/<int:pk>/update/', ItemUpdateView.as_view(), name='item-update'), 
    # '/item/int:pk/delete/' 动态 URL，捕获物品 ID，映射到 ItemDeleteView 类视图，用于删除指定物品
    path('item/<int:pk>/delete/', ItemDeleteView.as_view(), name='item-delete'),
    # '/item/int:pk/unavailable/' 动态 URL，捕获物品 ID，映射到 mark_unavailable 视图函数，用于将物品标记为不可用状态
    path('item/<int:pk>/unavailable/', mark_unavailable, name='item-unavailable'),

    path('register/', register, name='register'), # '/register/' URL 映射到 register 视图函数，用于用户注册
    path('profile/', profile, name='profile'), # '/profile/' URL 映射到 profile 视图函数，用于查看/编辑用户资料
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),  # '/logout/' URL 映射到 Django 内置的 LogoutView，登出后重定向到首页
]