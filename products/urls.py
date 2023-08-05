from django.urls import path
from .views import *

urlpatterns = [
   path('', index, name='index'),
   path('shop', shop, name='shop'),
   path('about-us', about_us, name='about_us'),
   path('contact-us', contact_us, name='contact_us'),
   path('searched', searched, name='searched'),
   path('product_details<int:product_id>', product_details, name='product_details'),
   path('offer_management', offer_management, name="offer_management"),
   path('add_offer', add_offer, name="add_offer"),
   path('remove_offer/<int:offer_id>', remove_offer, name="remove_offer"),
   path('get_similar_products/', get_similar_products, name='get_similar_products'),
]
