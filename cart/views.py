from django.shortcuts import render,redirect
from products.models import Product
from cart.models import Cart,CartItem,Coupon
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import Address
from orders.models import Order,OrderItem
from django.http import JsonResponse
import random




@login_required(login_url='user_login')
def cart(request):
    cart_obj = Cart.objects.filter(is_paid=False, user=request.user).first()
    coupons = Coupon.objects.all().order_by('created_at')

    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__iexact=coupon).first()
        
        
        if not coupon_obj:
            messages.warning(request,'Invalid coupon.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.coupon:
            messages.warning(request,'Coupon already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total() < coupon_obj.minimum_amount:
            messages.warning(request,f"Amount should be greater than {coupon_obj.minimum_amount}")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj.is_expired:
            messages.warning(request,'Coupon has been expired.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        cart_obj.coupon = coupon_obj
        cart_obj.save()
        messages.success(request,'Coupon applied.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'cart_obj': cart_obj,
        'coupons':coupons
        }
    
    return render(request,'cart/cart.html',context)




@login_required(login_url='user_login')
def remove_coupon(request,cart_id):
    cart = Cart.objects.get(id=cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request,'Coupon removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
  



@login_required(login_url='user_login')
def add_to_cart(request,product_id):
    product = Product.objects.get(id = product_id)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

    if product.stock <= 0:
        messages.warning(request, 'This product is out of stock.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Check if the product already exists in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if created:
        messages.success(request, 'Product added to the cart.')   
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if not created:
        # If the product already exists, increment the quantity
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Product already in cart. increased the quantity.')
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Stock limit reached for this product.')
            
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


 

@login_required(login_url='user_login')
def remove_cart(request,cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
    except Exception as e:
        print(e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




#using ajax
@login_required(login_url='user_login')
def increment_quantity(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
        cart = cart_item.cart
        cart_total = cart.get_cart_total()
        item_price = cart_item.get_product_price()
        response_data = {  
            'quantity': cart_item.quantity,
            'cart_total': cart_total,
            'item_price' : item_price,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Stock limit reached for this product.'}, status=400)




#using ajax
@login_required(login_url='user_login')
def decrement_quantity(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        cart = cart_item.cart
        cart_total = cart.get_cart_total()
        item_price = cart_item.get_product_price()
        response_data = {
            'quantity': cart_item.quantity, 
            'cart_total': cart_total,
            'item_price' : item_price,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Quantity cannot be less than 1.'}, status=400)




@login_required(login_url='user_login')
def checkout(request):
    user_addresses = Address.objects.filter(user=request.user)
    
    user_cart = Cart.objects.filter(user=request.user, is_paid=False).last()
    cart_items = user_cart.cart_items.all()
    cart_total = user_cart.get_cart_total()

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'user_addresses':user_addresses,
    }
    return render(request,'cart/checkout.html',context)




@login_required(login_url='user_login')
def placeorder(request):
    if request.method == 'POST':
 
        address_id = request.POST.get('address')
        address_obj = Address.objects.get(id=address_id)
   
        neworder = Order()
        neworder.user = request.user
        neworder.full_name = request.POST.get('full_name')
        neworder.phone_number = request.POST.get('phone_number')
        neworder.address = address_obj

        neworder.payment_mode = request.POST.get('payment_mode')
        neworder.payment_id = request.POST.get('payment_id')

        # Get the user's cart and calculate the total price
        user_cart = Cart.objects.filter(user=request.user, is_paid=False).last()
        neworder.total_price = user_cart.get_cart_total()

        track_no = 'RR'+str(random.randint(1111111,9999999)) 

        while Order.objects.filter(tracking_no=track_no).exists():
            track_no = 'RR'+str(random.randint(1111111,9999999)) 

        neworder.tracking_no = track_no
        neworder.save()

        # Add cart items to order items and decrease product stock
        cart_items = user_cart.cart_items.all()

        for cart_item in cart_items:
            order_item = OrderItem()
            order_item.order = neworder
            order_item.product = cart_item.product
            order_item.price = cart_item.product.price * cart_item.quantity
            order_item.quantity = cart_item.quantity
            order_item.save()

            # Decrease the product stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Delete the cart
        user_cart.delete()

        context = {'neworder':neworder}
        # return render(request,'cart/order_confirmation.html',context)


        payMode = request.POST.get('payment_mode')
        if (payMode == "Paid by Razorpay"):
            return JsonResponse({'status':"Your order has been placed successfully."})
    return redirect('orders')    




def razorpaycheck(request):
    cart = Cart.objects.get(user=request.user,is_paid=False)
    total_price = cart.get_cart_total()

    return JsonResponse({
        'total_price':total_price
    })




#adminside
def coupon_list(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    context = {
        'coupons':coupons
    }
    return render(request,'cart/coupon_list.html',context)




#adminside
def create_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST['coupon_code']
        minimum_amount = request.POST['minimum_amount']
        discount_price = request.POST['discount_price']

        if coupon_code.strip() == '':
            messages.error(request,'Add coupon code correctly.')
            return redirect('create_coupon')
        coupon = Coupon.objects.create(
            coupon_code = coupon_code,
            minimum_amount = minimum_amount,
            discount_price = discount_price,
        )
        messages.success(request,'New coupon is created.')
        return redirect('coupon_list')
    
    return render(request,'cart/create_coupon.html')




#adminside
def delete_coupon(request,coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon_code = coupon.coupon_code  #
    coupon.delete()
    messages.warning(request, f"Coupon {coupon_code} deleted successfully.")
    return redirect('coupon_list')




#adminside 
def edit_coupon(request,coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)

    if request.method == "POST":
        coupon_code = request.POST['coupon_code']
        minimum_amount = request.POST['minimum_amount']
        discount_price = request.POST['discount_price']

        if 'is_expired' in request.POST:
            is_expired = True
        else:
            is_expired = False

        if coupon_code.strip() == "":
            messages.error(request,'blank value not allowed.') 
            return redirect('edit_coupon', coupon_id=coupon.id)
        
        coupon.coupon_code = coupon_code
        coupon.minimum_amount = minimum_amount
        coupon.discount_price = discount_price
        coupon.is_expired = is_expired
        coupon.save()

        messages.success(request,'Coupon edited successfully.')
        return redirect('coupon_list')
        
           
    context = {
        'coupon':coupon,
    }
    return render(request,'cart/edit_coupon.html',context)