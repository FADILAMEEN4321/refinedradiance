from django.urls import path
from .views import *



urlpatterns = [
    
    #cart, checkout, placeorder.
    path('cart',cart,name='cart'),
    path('add_to_cart/<int:product_id>/',add_to_cart,name='add_to_cart'),
    path('remove_cart/<int:cart_item_id>/',remove_cart,name='remove_cart'),
    path('remove_coupon/<int:cart_id>/',remove_coupon,name='remove_coupon'),
    path('increment_quantity/<int:cart_item_id>/', increment_quantity, name='increment_quantity'),
    path('decrement_quantity/<int:cart_item_id>/', decrement_quantity, name='decrement_quantity'),
    path('checkout',checkout,name='checkout'),
    path('placeorder',placeorder,name='placeorder'),
    
    #razorpay
    path('proceed-to-pay', razorpaycheck, name="proceed-to-pay"),

    #coupon management.
    path('coupon_list', coupon_list , name="coupon_list"),
    path('create_coupon', create_coupon , name="create_coupon"),
    path('delete_coupon/<int:coupon_id>', delete_coupon , name="delete_coupon"),
    path('edit_coupon<int:coupon_id>', edit_coupon , name="edit_coupon"),

]
