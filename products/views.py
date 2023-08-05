from django.shortcuts import render,redirect
from .models import *
from django.utils import timezone
from django.contrib import messages
from products.models import Offer
from django.http import JsonResponse

   
def custom_404_page(request, exception):
    return render(request, '404.html', status=404)



def about_us(request):
    return render(request,'products/about_us.html')



def contact_us(request):
    return render(request,'products/contact_us.html')



def index(request):
    bestsellers = Product.objects.all()[:10]
    new_arrivals = Product.objects.filter(created_at__lte=timezone.now()).order_by('-created_at')[:12]
    hero_banners = Banner.objects.all()[:2]
    potrait_banners = Banner.objects.all()[2:5]
    bottom_banners = Banner.objects.all()[5:7]
    brand_logos = BrandLogo.objects.all()
    

    # Retrieve the list of recently viewed product IDs from the session
    recently_viewed = request.session.get('recently_viewed', [])

    # Initialize an empty list to store recently viewed products
    recently_viewed_products = []

    # Loop through each product ID and fetch the corresponding product objects
    for product_id in recently_viewed:
      try:
        product = Product.objects.get(id=product_id)
        recently_viewed_products.append(product)
      except Product.DoesNotExist:
        # Handle the case where the product does not exist in the database
        pass

    
    context = {
     'bestsellers':bestsellers,
     'new_arrivals':new_arrivals,
     'hero_banners':hero_banners,
     'potrait_banners':potrait_banners,
     'bottom_banners':bottom_banners,
     'brand_logos':brand_logos ,
     'sorted_recently_viewed_products': recently_viewed_products,
     
    }
    
    return render(request,'products/index.html',context)



def get_similar_products(request):  
    if request.method == 'GET':
        search_term = request.GET.get('search_term', '')
        # Query the database to get similar products based on the search_term
        # For example:
        similar_products = Product.objects.filter(name__icontains=search_term)[:10]
        data = {
            'products': [{'id': product.id, 'name': product.name} for product in similar_products]
        }
        return JsonResponse(data)
    return JsonResponse({}, status=400)



def shop(request):
    products = Product.objects.all().select_related('brand').prefetch_related('images').order_by('-created_at')
    products_count = products.count()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    context ={
        'products':products,
        'products_count':products_count,
        'categories':categories,
        'brands':brands,      
      }
    return render(request,'products/shop.html',context)

   

def product_details(request,product_id):
    product_obj = Product.objects.get(id=product_id)

    # Get the list of recently viewed product IDs from the session
    recently_viewed = request.session.get('recently_viewed', [])

    # Create a copy of the recently viewed list
    updated_recently_viewed = recently_viewed[:]

    # If the product is already in the list, remove it to move it to the top
    if product_id in updated_recently_viewed:
        updated_recently_viewed.remove(product_id)

    # Add the product ID to the beginning of the list
    updated_recently_viewed.insert(0, product_id)

    # Limit the list to the most recent 10 viewed products
    updated_recently_viewed = updated_recently_viewed[:10]

     # Save the updated list back to the session
    request.session['recently_viewed'] = updated_recently_viewed


    return render(request,'products/single_product.html',{'product_obj':product_obj})



def searched(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        products = Product.objects.filter(name__icontains= searched)
    if request.method == 'GET':
        searched = request.GET.get('searched')
        products = Product.objects.filter(name__iexact= searched)
    
    context = {
        'products': products
    }

    return render(request,'products/searched.html', context)


#adminside offer management.
def offer_management(request):
    offers = Offer.objects.all()
    context = {
        'offers':offers
    }
    return render(request,'adminside/offers.html',context)



def add_offer(request):
    if request.method == 'POST':
        offer_name = request.POST['offer_name']
        discount_percentage = request.POST['discount_percentage']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        if offer_name.strip=='':
            messages.error(request,'Fields cannot be blank.')
            return redirect('add_offer')
        
        if Offer.objects.filter(name=offer_name).exists():
            messages.error(request,'Offer name already exists.')
            return redirect('add_offer')
        
        offer = Offer.objects.create(
                name=offer_name,
                discount_percentage=discount_percentage,
                start_date=start_date,
                end_date=end_date
                )
        messages.success(request, f'Offer "{offer.name}" has been added successfully.')
        return redirect('add_offer')


    return render(request,'adminside/add_offer.html')



def remove_offer(request,offer_id):
    offer = Offer.objects.get(id=offer_id).delete()
    messages.warning(request,'Offer has been removed successfully.')
    return redirect('offer_management')

