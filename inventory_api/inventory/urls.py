from django.urls import path
from .views import (
  RegisterView,
  UserListCreateView,
  UserRetrieveUpdateDestroyView,
  CategoryListCreateView,
  CategoryRetrieveUpdateDestroyView,
  InventoryItemListCreateView,
  InventoryItemRetrieveUpdateDestroyView,
  InventoryLevelView,
  InventoryChangeLogListView,
)

urlpatterns = [
  # auth
  path('auth/register/', RegisterView.as_view(), name='register'),

  # users
  path('users/', UserListCreateView.as_view(), name='user-list'),
  path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),

  # categories
  path('categories/', CategoryListCreateView.as_view(), name='category-list'),
  path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),

  # inventory
  path('inventory/', InventoryItemListCreateView.as_view(), name='inventory-list'),
  path('inventory/levels/', InventoryLevelView.as_view(), name='inventory-levels'),
  path('inventory/logs/', InventoryChangeLogListView.as_view(), name='inventory-logs'),
  path('inventory/<int:pk>/', InventoryItemRetrieveUpdateDestroyView.as_view(), name='inventory-detail'),
  # per-item logs: view expects `item_pk` kwarg
  path('inventory/<int:item_pk>/logs/', InventoryChangeLogListView.as_view(), name='inventory-item-logs'),
]