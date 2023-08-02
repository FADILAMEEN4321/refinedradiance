from django.db import models
from accounts.models import UserProfile
from products.models import Product

# Create your models here.

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)
    created_at = models.DateTimeField(auto_now_add=True)

    

class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True,blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = 0
        for cart_item in cart_items:
            price += cart_item.get_product_price()

        if self.coupon:
            if self.coupon.minimum_amount < price:
              return price - self.coupon.discount_price
    
        return price
         
    
   
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null= True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_product_price(self):
        # Calculate the discounted price using the discounted_price method of the associated product
        discounted_price = self.product.discounted_price()
        
        # Return the total price after applying the offer discount
        return discounted_price * self.quantity
    
    def get_product_image(self):
        return self.product.images.first().image.url
    
    class Meta:
        ordering = ['created_at']
    