from django.db import models
from accounts.models import UserProfile
from products.models import Product

# Create your models here.


class Wishlist(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_wishlist_product_image(self):
        return self.product.images.first().image.url
    
    