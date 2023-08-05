from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from accounts.models import UserProfile
from django.contrib.auth.models import AnonymousUser




class Offer(models.Model):
    name = models.CharField(max_length=200)
    discount_percentage = models.DecimalField(max_digits=5,decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return self.name   


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    offers = models.ManyToManyField(Offer, blank=True, related_name='categories')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'categories'
    


class Brand(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True) 
    description = models.TextField(max_length=500, blank=True)
    specifications = models.TextField(blank=True)  
    price = models.DecimalField(max_digits=8, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products') 
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True) 
    offers = models.ManyToManyField(Offer, blank=True, related_name='products')

    
    # method to get the price of a product after offer discounts.
    def discounted_price(self):
        product_discount = 0
        category_discount = 0

        # Check for product-level offers
        if self.offers.exists():
            max_product_discount = max(self.offers.all(), key=lambda offer: offer.discount_percentage)
            product_discount = max_product_discount.discount_percentage
        
        # Check for category-level offers
        if self.category.offers.exists():
            max_category_discount = max(self.category.offers.all(), key=lambda offer: offer.discount_percentage)
            category_discount = max_category_discount.discount_percentage
        
        # Use product-level discount if it exists, otherwise use category-level discount
        max_discount = product_discount if product_discount > 0 else category_discount

        # Calculate the discounted price based on the maximum discount percentage
        discounted_price = float(self.price) * (1 - float(max_discount) / 100)

        return discounted_price
    

    # method to get the offer dis percentage of a product.
    def get_max_discount_percentage(self):
        product_discount = 0
        category_discount = 0

        # Check for product-level offers
        if self.offers.exists():
            max_product_discount = max(self.offers.all(), key=lambda offer: offer.discount_percentage)
            product_discount = max_product_discount.discount_percentage

        # Check for category-level offers
        if self.category.offers.exists():
            max_category_discount = max(self.category.offers.all(), key=lambda offer: offer.discount_percentage)
            category_discount = max_category_discount.discount_percentage

        # Use product-level discount if it exists, otherwise use category-level discount
        max_discount = int(max(product_discount, category_discount))

        return max_discount
          

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  
        super().save(*args, **kwargs)




class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)

   

class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')  
    
    def __str__(self):
        return self.title  



class BrandLogo(models.Model):
    brand_id = models.ForeignKey(Brand, on_delete=models.CASCADE,  related_name='brand')
    name = models.CharField(max_length=100)
    logo  = models.ImageField(upload_to='images/') 

    def __str__(self):
        return self.name 


   



  