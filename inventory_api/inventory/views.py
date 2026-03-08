from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import filters, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.models import User
from django.db.models import F, Sum, Count
from django_filters.rest_framework import DjangoFilterBackend


from .models import Category, InventoryItem, InventoryChangeLog
from .serializers import (UserSerializer, CategorySerializer, InventoryItemSerializer,InventoryItemCreateSerializer,
                          InventoryItemUpdateSerializer, InventoryChangeLogSerializer,InventoryLevelSerializer)
from .filters import InventoryItemFilter
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsSelfOrAdmin


#Auth
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

#Users
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['username',  'date_joined']

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

#Categories
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

#Inventory Items
class InventoryItemListCreateView(generics.ListCreateAPIView):
    queryset = InventoryItem.objects.select_related('category', 'created_by'). all()
    permission_classes = [IsAuthenticated ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InventoryItemFilter
    search_fields = ['name','description','category__name']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == ['POST']:
            return InventoryItemCreateSerializer
        return InventoryItemSerializer
    
    def perform_create(self,serializer):
        serializer.save(created_by=self.request.user)

class InventoryItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryItem.objects.select_related('category','created_by').all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT','PATCH']:
            return InventoryItemUpdateSerializer
        return InventoryItemSerializer
       
#inventory levels
class InventoryLevelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_items = InventoryItem.objects.all()
        queryset = all_items

        category = request.query_params.get('category')
        low_stock = request.query_params.get('low_stock')
        stock_status = request.query_params.get('stock_status')

        if category:
            queryset = queryset.filter(category__name__icontains=category)
            if low_stock == 'true':
                queryset = queryset.filter(quantity__lte=F('low_stock_threshold'))
            if stock_status == 'out_of_stock':
                queryset = queryset.filter(quantity=0)
            elif stock_status == 'in stock':
                queryset = queryset.filter(quantity__gt=F('low_stock_threshold'))

        total_value = sum(i.quantity * i.price for i in all_items)

        data = {
                'summary': {
                'total_items' : all_items.count(),
                'total_quantity': all_items.aggregate(t=Sum('quantity'))['t'] or 0,
                'total_value': round(float(total_value),2),
                'out_of_stock': all_items.filter(quantity=0).count(),
                'low_stock': all_items.filter(quantity__lte=F('low_stock_threshold')).count(),
                },
                'items':InventoryLevelSerializer(queryset, many=True).data,
            }
        return Response(data, status=status.HTTP_200_OK)
        
#Change Logs
class InventoryChangeLogListView(generics.ListAPIView):
    serializer_class = InventoryChangeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = [ '-timestamp']

    def get_queryset(self):
        item_pk = self.kwargs.get('item_pk')
        qs = InventoryChangeLog.objects.select_related('item','changed_by').all()
        if item_pk:
            qs = qs.filter(item__pk=item_pk)
        return qs
    
