from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, InventoryItem, InventoryChangeLog

# User Serializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_staff', 'date_joined']
        read_only_fields = ['is_staff','date_joined']

    def create (self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields =['id', 'name', 'description', 'created_at', 'item_count']

    def get_item_count(self, obj):
        return obj.items.count()

# Inventory Item Serializer
class InventoryItemSerializer(serializers.ModelSerializer):
    stock_status = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    created_by = serializers.ReadOnlyField(source= 'created_by.username')
    category_name = serializers.ReadOnlyField(source = 'category.name')    

    class Meta :
        model= InventoryItem
        fields = [
            'id', 'name', 'description', 'quantity', 'price', 'category', 'category_name', 
            'low_stock_threshold','stock_status','is_low_stock','created_by', 'date_added', 'last_updated'
        ]
        read_only_fields = ['date_added', 'last_updated']

        def validate_quantity(self, value):
            if value < 0:
                raise serializers.ValidationError('Quantity cannot be negative.')
            return value
        
        def validate_price(self, value):
            if value < 0:
                raise serializers.ValidationError('Price cannot be negative.')
            return value
        

class InventoryItemCreateSerializer(InventoryItemSerializer):
    def create (self, validated_data):
        item = super().create(validated_data)
        InventoryChangeLog.objects.create(
            item= item,
            changed_by = item.created_by,
            change_type = 'creation',
            previous_quantity = 0,
            new_quantity = item.quantity,
            note= 'Item created. ' ,
        )
        return item
    

      