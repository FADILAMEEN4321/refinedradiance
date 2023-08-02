from django.db import models
from accounts.models import UserProfile,Address
from products.models import Product



# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, null=False)
    phone_number = models.CharField(max_length=150, null=False)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL,null=True)
    total_price = models.FloatField(null=True)
    payment_mode = models.CharField(max_length=250,null=True)
    order_status = (
        ('Pending','Pending'),
        ('Out For Shipping','Out For Shipping'),
        ('Completed','Completed'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=150, choices=order_status, default='Pending')
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=150, null=True)
    refund_amount = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.tracking_no)
    
    def refund_on_cancel(self):
        # Calculate the refund amount 
        refund_amount = self.total_price
        # Update the user's wallet balance
        self.user.wallet += refund_amount
        self.user.save()
        # Update the order status and refund amount
        self.refund_amount = refund_amount
        self.save()
        



 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)
    return_item = models.OneToOneField('ReturnItem', on_delete=models.SET_NULL, null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} - {}'.format(self.order.id, self.order.tracking_no)
    
    def get_orderitem_product_image(self):
        return self.product.images.first().image.url
    
    class Meta:
        ordering = ['created_at']
    

    

class ReturnItem(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    return_reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)   


    def refund_on_return(self):
        refund_amount = self.order_item.price 

        # Retriving the user associated with the order item
        user = self.order_item.order.user
        
        # Update user's wallet balance
        user.wallet += refund_amount
        user.save()

