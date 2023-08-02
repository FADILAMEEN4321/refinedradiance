from django.shortcuts import render
from .models import *
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart,CartItem

# Create your views here.

@login_required(login_url='user_login')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request,'wishlist/wishlist.html',context)


@login_required(login_url='user_login')
def add_to_wishlist(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request,'Product added to Wishlist.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.warning(request,'Product already in wishlist.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




@login_required(login_url='user_login')    
def remove_from_wishlist(request, product_id):
    wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, 'Product removed from Wishlist.')
    else:
        messages.warning(request, 'Product not found in Wishlist.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



   
        



