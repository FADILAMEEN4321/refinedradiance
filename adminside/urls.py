from django.urls import path
from .views import *

urlpatterns = [

    path('dashboard',dashboard, name='dashboard'),

    #user management
    path('user_management',user_management, name='user_management'),
    path('block-unblock-user/<int:user_id>',block_unblock_user, name='block_unblock_user'),

    #product management
    path('product_list',product_list, name='product_list'),
    path('add_products',add_products, name='add_products'),
    path('delete_products/<int:product_id>',delete_products, name='delete_products'),
    path('edit_products<int:product_id>',edit_products, name='edit_products'),
    path('product_image_management',product_image_management, name='product_image_management'),
    path('delete_image/<int:image_id>', delete_image, name="delete_image"),

    #category managment
    path('category_management',category_management, name='category_management'),
    path('add_category',add_category, name='add_category'),
    path('delete_category/<int:category_id>',delete_category, name='delete_category'),
    path('edit_category<int:category_id>',edit_category, name='edit_category'),


    #brand managment
    path('brand_management',brand_management, name='brand_management'),
    path('add_brand',add_brand, name='add_brand'),
    path('delete_brand/<int:brand_id>',delete_brand, name='delete_brand'),
    path('edit_brand<int:brand_id>',edit_brand, name='edit_brand'),


    #banner managment
    path('add_banner',add_banner, name='add_banner'),


    #image managment
    path('add_image',add_image, name='add_image'),


]

