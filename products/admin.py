from django.contrib import admin
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_dispaly = ('name',)
admin.site.register(Category, CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)    
admin.site.register(Brand, BrandAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category_id','brand_id','price','stock')
admin.site.register(Product, ProductAdmin)

admin.site.register(Image)
admin.site.register(Banner)
admin.site.register(BrandLogo)
admin.site.register(Offer)

