from django.urls import path
from .views import *



urlpatterns = [
      
      #user authentication.
      path('login', user_login, name='user_login'),
      path('logout', user_logout, name='user_logout'),
      path('signup', user_sigup, name='user_signup'),


      #forgot password.
      path('forgot-password', forgot_password, name='forgot_password'),
      path('reset/<str:uidb64>/<str:token>/', reset_password_confirm, name='password_reset_confirm'),
      path('reset-password', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),


      #phone otp verification.
      path('otp-login', otp_login, name="otp_login"),
      path('verify-otp<int:phone_number>', verify_otp, name="verify_otp"),


      #urls related to USER PROFILE.
      path('profile', profile, name='profile'),
      path('edit_profile/', edit_profile, name='edit_profile'),
      path('address', address, name='address'),
      path('add_address', add_address, name='add_address'),
      path('add_order_address', add_order_address, name='add_order_address'),
      path('edit_address<int:address_id>', edit_address, name='edit_address'),
      path('delete_address/<int:address_id>', delete_address, name='delete_address'),
      path('change_password/', change_password, name='change_password/'),
      path('orders', orders, name='orders'),
      path('cancel_user_order/<int:order_id>', cancel_user_order, name='cancel_user_order'),
      path('order_details<int:order_id>', order_details, name='order_details'),
      path('return_order_item/<int:order_item_id>', return_order_item, name='return_order_item'),
#     path('remove_address/<int:address_id>', remove_address ,name="remove_address"),
      path('order_invoice/<int:order_id>', download_invoice, name='order_invoice'),


]    

