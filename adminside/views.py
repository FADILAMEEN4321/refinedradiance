from django.shortcuts import render,redirect
from accounts.models import UserProfile
from products.models import Product,Brand,Category
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from products.forms import BannerForm,Image
from django.contrib.auth import logout,get_user_model
from products.models import Offer,Product
from orders.models import Order,OrderItem
from django.db.models import Sum,DateTimeField,Count
from django.db.models.functions import TruncMonth
import json
from datetime import datetime, timedelta


# <=============================== Dashboard management ==========================================>
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('index')
    
    # Calculating total revenue
    total_revenue = Order.objects.aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0
    # Calculating total orders
    total_orders = Order.objects.count()
    # Calculating total products
    total_products = Product.objects.count()
    # Calculating total category
    total_categories = Category.objects.count()
    # Calculating monthly income
    monthly_income = Order.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total_income=Sum('total_price')).order_by('month')
    # Calculate total users
    total_users = UserProfile.objects.count()
      
    # Perform the query to get payment mode counts
    payment_mode_counts = Order.objects.values('payment_mode').annotate(order_count=Count('id'))

    # Extract labels and data for the transaction chart.
    labels = [item['payment_mode'] for item in payment_mode_counts]
    data = [item['order_count'] for item in payment_mode_counts]  


    # Query to get the count of orders for each order status
    order_status_counts = Order.objects.values('status').annotate(order_count=Count('status'))
    

    # Extract labels and data for the chart
    order_labels = [item['status'] for item in order_status_counts]
    order_data = [item['order_count'] for item in order_status_counts]


    # Calculate the last 6 months from the current date
    today = datetime.now()
    last_six_months = [today.strftime('%B')]  # Initialize the list with the current month
    for i in range(1, 6):
        previous_month = today - timedelta(days=30*i)
        last_six_months.append(previous_month.strftime('%B'))


    # Calculate total sales for each of the last six months
    total_sales_data = []
    for i in range(6):
        start_date = today - timedelta(days=30*(i+1))
        end_date = today - timedelta(days=30*i)
        total_sales = Order.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        total_sales_data.append(total_sales)


    # Calculate total visitors for each of the last six months
    total_visitors_data = []
    for i in range(6):
        start_date = today - timedelta(days=30*(i+1))
        end_date = today - timedelta(days=30*i)
        total_visitors = UserProfile.objects.filter(date_joined__gte=start_date, date_joined__lt=end_date).count()
        total_visitors_data.append(total_visitors)      

 
    # Get all categories
    categories = Category.objects.all() 
    
    # Calculate the sales for each category
    category_sales_data = []
    category_names = []
    for category in categories:
        category_names.append(category.name)
        total_sales = OrderItem.objects.filter(product__category=category, order__status='Completed').aggregate(total_sales=Sum('quantity'))['total_sales'] or 0
        category_sales_data.append(total_sales)
    
    
    top_selling_products = OrderItem.objects.filter(is_returned=False).values('product__name').annotate(sales_count=Count('product')).order_by('-sales_count')[:3]
    
    # Create two lists to store product names and sales counts
    product_names = []
    sales_counts = []
    

    # Extract data from 'top_selling_products' and populate the lists
    for product in top_selling_products:
        shortened_name = shorten_product_name(product['product__name'])
        product_names.append(shortened_name)
        sales_counts.append(product['sales_count'])


    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_categories': total_categories,
        'monthly_income': monthly_income,
        'total_users': total_users,
        
        'labels': labels,
        'data': data,
        
        'months': last_six_months,
        'total_sales_data': total_sales_data,
        'total_visitors_data': total_visitors_data, 

        'order_labels': order_labels,
        'order_data': order_data,

        'category_sales_data': category_sales_data,
        'category_names': category_names,

        'product_names': product_names,
        'sales_counts': sales_counts,

    }

    return render(request,'adminside/dashboard.html',context)



# Function to shorten product names (truncate to a certain length)
def shorten_product_name(name, max_length=9):
    if len(name) <= max_length:
        return name
    return name[:max_length - 2] + '..'





# <=============================== User management ===========================================>

@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def user_management(request):
    
    if not request.user.is_superuser:
        return redirect('index')

    if request.method == 'POST':
        searched = request.POST['searched']
        searched_users = UserProfile.objects.filter(first_name__istartswith=searched).order_by('first_name')
        return render(request,'adminside/user_management.html',{'searched_users':searched_users})
    
    users = UserProfile.objects.all().order_by('first_name')
    return render(request,'adminside/user_management.html',{'users':users})


@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def block_unblock_user(request, user_id):
    
    if not request.user.is_superuser:
        return redirect('index')

    user = UserProfile.objects.get(id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
  
    return redirect('user_management')



# <================================ Product management =======================================>

@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def product_list(request):

    if not request.user.is_superuser:
        return redirect('index')

    products = Product.objects.all()
    return render(request,'adminside/product_list.html',{'products':products})


@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def add_products(request):
    
    if not request.user.is_superuser:
        return redirect('index')

    brands = Brand.objects.all()
    categories = Category.objects.all()
    context = {
        'brands':brands,
        'categories':categories,
    }
    if request.method == 'POST':
        name = request.POST['product_name']
        description = request.POST['description']
        brand_id = request.POST['brand_name']
        price = request.POST['price']
        stock = request.POST['stock']
        category_id = request.POST['category']

        if name.strip() == '':
            messages.error(request,'Enter name correctly.')
            return HttpResponseRedirect(request.path_info)

        if Product.objects.filter(name=name).exists():
            messages.error(request,'Product name already exists.')
            return HttpResponseRedirect(request.path_info)
        
        if description.strip() == '':
            messages.error(request,'Enter description correctly.')
            return HttpResponseRedirect(request.path_info)
        
        brand_obj = Brand.objects.get(id=brand_id)
        category_obj = Category.objects.get(id=category_id)
        
        Product.objects.create(
            name=name,
            description=description,
            price=price,
            brand=brand_obj,
            category=category_obj,
            stock=stock
            )
         
        messages.success(request,'A new product created successfully.')
        return HttpResponseRedirect(request.path_info)
             
    return render(request,'adminside/add_product.html',context)




@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def delete_products(request,product_id):

    if not request.user.is_superuser:
        return redirect('index')

    product_obj = get_object_or_404(Product,id=product_id)
    product_name = str(product_obj)
    product_obj.delete()
    messages.warning(request,f'Product {product_name} deleted successfully.')
    return redirect('product_list')




@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def edit_products(request,product_id):

    if not request.user.is_superuser:
        return redirect('index')

    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    offers = Offer.objects.all()

    if request.method == 'POST':
        name = request.POST['product_name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']
        category_id = request.POST['category']
        offer_id = request.POST['offer_id']

        if name.strip() == '':
            messages.error(request,'Enter name correctly.')
            return HttpResponseRedirect(request.path_info)
        
        if description.strip() == '':
            messages.error(request,'Enter description correctly.')
            return HttpResponseRedirect(request.path_info)
        
        category_obj = Category.objects.get(id=category_id)
        offer = Offer.objects.get(id=offer_id)

        product.name = name
        product.description = description
        product.price = price
        product.stock = stock
        product.category = category_obj

        #adding offer to the product.
        product.offers.add(offer)

        product.save()
        messages.success(request,'Product has been edited successfully.')
        return redirect('edit_products', product_id=product.id)

    context = {
        'categories':categories,
        'product':product,
        'offers':offers
    }
    return render(request,'adminside/edit_products.html',context)




# <================================ Category management ====================================>    

@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def category_management(request):
    if not request.user.is_superuser:
        return redirect('index')
    categories = Category.objects.all()
    return render(request,'adminside/category_management.html',{'categories':categories})




@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def add_category(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        name = request.POST['category_name']
        description = request.POST['description']

        if Category.objects.filter(name=name).exists():
            messages.error(request,'Category name already exists.')
            return HttpResponseRedirect(request.path_info)
        if name.strip()==''or description.strip()=='':
            messages.error(request,'Fields cannot be empty.')
            return HttpResponseRedirect(request.path_info)
        
        Category.objects.create(name=name,description=description)
        messages.success(request,'New Category created successfully.')
        return HttpResponseRedirect(request.path_info)
             
    return render(request,'adminside/add_category.html')




@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def delete_category(request,category_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    category_obj = Category.objects.get(id=category_id)
    category_name = str(category_obj)
    category_obj.delete()
    messages.warning(request,f'{category_name} category deleted.')
    return redirect('category_management')




@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def edit_category(request,category_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    category = Category.objects.get(id=category_id)
    offers = Offer.objects.all()

    if request.method == 'POST':
        name = request.POST['category_name']
        description = request.POST['description']
        offer_id = request.POST['offer_id']

        if Category.objects.filter(name=name).exists() and category.name != name:
            messages.warning(request,'Category name already exists.')
            return HttpResponseRedirect(request.path_info)
        
        
        offer = Offer.objects.get(id=offer_id) 

        category.name = name
        category.description = description

        #adding offer to the category.
        category.offers.add(offer)
        category.save()
        messages.success(request,'Category edited successfully')
        return redirect('edit_category',category_id=category.id)
    
    context = {
        'category':category,
        'offers':offers
    }
            

    return render(request,'adminside/edit_category.html',context)




# <================================== Brand management =====================================> 

@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def brand_management(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    brands = Brand.objects.all().order_by('id')
    return render(request,'adminside/brand_management.html',{'brands':brands}) 




@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def add_brand(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        name = request.POST['brand_name']

        if Brand.objects.filter(name=name).exists():
            messages.error(request,'Brand name already exists.')
            return HttpResponseRedirect(request.path_info)
        if name.strip()=='':
            messages.error(request,'Field cannot be empty.')
            return HttpResponseRedirect(request.path_info)
        
        Brand.objects.create(name=name)
        messages.success(request,'New Brand added successfully.')
        return HttpResponseRedirect(request.path_info)
             
    return render(request,'adminside/add_brand.html')



@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def delete_brand(request,brand_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    brand_obj = Brand.objects.get(id=brand_id)
    brand_name = str(brand_obj)
    brand_obj.delete()
    messages.warning(request,f'{brand_name} brand deleted.')
    return redirect('brand_management')



@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def edit_brand(request,brand_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    brand = Brand.objects.get(id=brand_id)
    if request.method == 'POST':
        name = request.POST['brand_name']

        if Brand.objects.filter(name=name).exists():
            messages.warning(request,'Brand name already exists.')
            return HttpResponseRedirect(request.path_info)
        brand.name = name
        brand.save()
        messages.success(request,'Category edited successfully')
        return redirect('edit_brand',brand_id=brand.id)
            
    return render(request,'adminside/edit_brand.html',{'brand':brand})



# <================================= Banner management ======================================> 

@cache_control(no_cache=True, must_revalidate=True,no_store=True) 
@login_required(login_url='user_login')   
def add_banner(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Banner created successfully.')
            return redirect('add_banner') 
    else:
        form = BannerForm()
    
    context = {'form': form}
    return render(request, 'adminside/add_banner.html', context)




# <=================================== Image management ======================================> 

@cache_control(no_cache=True, must_revalidate=True,no_store=True) 
@login_required(login_url='user_login') 
def add_image(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        image = request.FILES.get('image')
        product_id = request.POST.get('product')

         
        image_obj = Image(image=image, product_id=product_id)
        image_obj.save()

        messages.success(request, 'Image added successfully.')
        return redirect('add_image')  

    products = Product.objects.all().order_by('name')
    return render(request, 'adminside/add_image.html', {'products': products})




@login_required(login_url='user_login')
def product_image_management(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    products = Product.objects.all()
    context = {
        'products':products
    }
    return render(request,'adminside/all_product_images.html',context)




@login_required(login_url='user_login')
def delete_image(request,image_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    image = Image.objects.get(id=image_id).delete()
    messages.warning(request,'Image deleted successfully.')
    return redirect('product_image_management')

    

