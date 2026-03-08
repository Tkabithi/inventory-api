import django_filters
from .models import InventoryItem
from django.db.models import F

class InventoryItemFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    max_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    stock_status = django_filters.CharFilter(method='filter_stock_status')

    class Meta:
        model = InventoryItem
        fields = ['name', 'category', 'min_price', 'max_price', 'min_quantity', 'max_quantity','stock_status']

    def filter_stock_status(self ,queryset, name, value):
        if value:
           return queryset.filter(quantity__lte = F('low_stock_threshold'))
        return queryset 
        