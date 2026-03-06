from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    low_stock_threshold = models.PositiveIntegerField(default=10)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name='inventory_items')
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.low_stock_threshold:
            return 'low_stock'
        else:
            return 'in_stock'
        

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold 
    
class InventoryChangeLog(models.Model):
    CHANGE_TYPE = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('update', 'Manual Update'),
        ('creation', 'Creation'),
    ]
    item= models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='change_logs')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'inventory_changes')
    change_type= models.CharField(max_length=20, choices=CHANGE_TYPE,default = 'update')
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    quantity_delta = models.IntegerField()
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        self.quantity_delta = self.new_quantity - self.previous_quantity
        super().save(*args, **kwargs)       
    
