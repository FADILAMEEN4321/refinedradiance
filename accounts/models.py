from django.db import models
from django.contrib.auth.models import AbstractUser


#Model used for user authentication and storing user specific details.
class UserProfile(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='images/', blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    wallet = models.FloatField(default=0)
    mobile_otp = models.CharField(max_length=6, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    # method to get number of cart items.
    def get_cart_count(self):
        from cart.models import CartItem
        return CartItem.objects.filter(cart__is_paid=False, cart__user=self).count()
    
    # method to get number of wishlist items.
    def get_wishlist_count(self):
        from wishlist.models import Wishlist
        return Wishlist.objects.filter(user=self).count()
    
    class Meta:
        db_table = 'userprofile'
 


class Address(models.Model):
    full_name = models.CharField(max_length=100, null=True)
    contact_number = models.CharField(max_length=12, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE) #relation to UserProfile model
    house_name = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return self.house_name




  