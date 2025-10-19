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
    path('', home, name='home'),
    path('items/', ItemListView.as_view(), name='item-list'),
    path('my-items/', UserItemListView.as_view(), name='user-item-list'),
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('item/new/', ItemCreateView.as_view(), name='item-create'),
    path('item/<int:pk>/update/', ItemUpdateView.as_view(), name='item-update'),
    path('item/<int:pk>/delete/', ItemDeleteView.as_view(), name='item-delete'),
    path('item/<int:pk>/unavailable/', mark_unavailable, name='item-unavailable'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),  # 退出后跳转首页
]