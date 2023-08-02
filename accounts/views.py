from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from .forms import Signup_form
from verify_email.email_handler import send_verification_email
from django.contrib.auth import get_user_model
from .models import Address
from orders.models import Order,OrderItem,ReturnItem
from products.models import Product
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import os
from django.conf import settings
from django.http import FileResponse
import random
from twilio.rest import Client
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str 
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import PasswordResetConfirmView
from django.conf import settings
from twilio.rest import Client








#------------------------------- User authentication ----------------------------------------->
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required(login_url='user_login')
def profile(request):
    user = request.user
    addresses = Address.objects.filter(user=user)

    context = {
        'addresses':addresses
    }

    return render(request,'account/profile.html',context)




def user_sigup(request):
    if request.method == 'POST':
       form = Signup_form(request.POST)
       if form.is_valid():
    
           #user activation email will be send and user will be saved.
           inactive_user = send_verification_email(request, form)
           messages.success(request,'A Verfication link has been sent to your Email. Please verify to login.')
           return redirect('user_login')
    else:
           form = Signup_form()

    context = {
        'form':form,
        }

    return render(request,'account/usersignup.html',context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticating the user using the ModelBackend
        user = authenticate(request, username=username, password=password)

        # Check if the user is authenticated successfully
        if user is not None:
            if user.is_active and not user.is_blocked:
                # Log the user in using Django's built-in login function
                login(request, user)

                # Checking if there's a 'next' parameter in the URL
                next_url = request.GET.get('next')

                if next_url:
                    # Redirect to the URL specified in the 'next' parameter
                    return redirect(next_url)
                else:
                    
                    return redirect('index')
            else:
                if not user.is_active:
                    messages.error(request, 'Verify your account.')
                    return HttpResponseRedirect(request.path_info)
                elif user.is_blocked:
                    messages.error(request, 'Your account has been blocked.')
                    return HttpResponseRedirect(request.path_info)
        else:
            messages.error(request, 'Invalid Email or Password.')
            return HttpResponseRedirect(request.path_info)

    return render(request, 'account/social/login.html')
 



@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    return redirect('index')




def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']  

        try:
            user = UserProfile.objects.get(email=email)  
            # Create a unique token for password reset
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            message = render_to_string('account/password_reset_email.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, message, 'from@example.com',[email])
            messages.success(request, 'Please check your email for the password reset link.')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
    return render(request, 'account/forgot_password.html')    




def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been successfully reset.')  
            return redirect('user_login')
        return render(request, 'account/reset_password.html')
    else:
        messages.error(request, 'Password reset link is invalid or has expired.')
        return redirect('forgot_password')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/reset_password.html'



def send_otp_on_phone(phone_number,otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to=phone_number,
        from_="+16817716393",
        body=f"Hi, Welcome to Refined Radiance your OTP is {otp}")

def generate_otp():
    return str(random.randint(100000, 999999))


def otp_login(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']

        user = UserProfile.objects.filter(phone_number=phone_number).first()
        if user:
            otp = generate_otp()
            user.mobile_otp = otp
            user.save()
            valid_phone_number= '+91' + phone_number
            send_otp_on_phone(valid_phone_number,otp)
            return redirect('verify_otp', phone_number=phone_number)
        
        else:
            messages.error(request,'You are not a registered user.')
            return redirect('otp_login')

    return render(request,'account/otp_login.html')


def verify_otp(request,phone_number):
    if request.method == 'POST':
        otp = request.POST['otp']
        user = UserProfile.objects.filter(phone_number=phone_number,mobile_otp= otp).first()
        

        if user :
            if user.is_active and not user.is_blocked:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('index')
            else:
                if not user.is_active:
                    messages.error(request, 'Verify your account.')
                    return redirect('user_login')
                elif user.is_blocked:
                    messages.error(request, 'Your account has been blocked.')
                    return redirect('user_login')
                
        else:
            messages.error(request,'OTP is incorrect.')
            return redirect('verify_otp', phone_number=phone_number)        


    return render(request,'account/verfiy_otp.html')    
    




#-------------------------------- Admin authentication -------------------------------------->
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)

        if user and user.is_superuser:
            login(request,user)
            return redirect('dashboard')
        
        messages.error(request,'Invalid Username or Password.')
        return redirect('admin_login')

    return render(request,'account/adminlogin.html')

@login_required(login_url='user_login')
def admin_logout(request):
    logout(request)
    return redirect('index')



#-------------------------------- User profile management -------------------------------------->
@login_required(login_url='user_login')
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')

        # Checking null values.
        if username.strip() == '' or first_name.strip() == '' or last_name.strip()=='':
            return HttpResponse('<div class="alert alert-danger alert-dismissible fade show" role="alert">Please type details correctly.</div>')

        #checking username already exists.    
        if UserProfile.objects.filter(username=username).exists() and user.username != username:
            return HttpResponse('<div class="alert alert-danger alert-dismissible fade show" role="alert">Username already exists.</div>')
        

        #checking phone number already exists.    
        if UserProfile.objects.filter(phone_number=phone_number).exists() and user.phone_number != phone_number:
            return HttpResponse('<div class="alert alert-danger alert-dismissible fade show" role="alert">Phone number already exists.</div>')


        # Update the user profile fields
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.save()
        return HttpResponse('<div class="alert alert-success alert-dismissible fade show" role="alert">Profile edited successfully.</div>')


@login_required(login_url='user_login')
def address(request):
    user = request.user
    user_profile = UserProfile.objects.get(id=user.id)
    addresses = Address.objects.filter(user=user_profile.id)
    return render(request,'account/address.html',{'addresses': addresses})


@login_required(login_url='user_login')
def add_address(request):
    user = request.user
    if request.method == 'POST':
        full_name = request.POST['full_name']
        contact_number = request.POST['contact_number']
        house_name = request.POST['house_name']
        landmark = request.POST['landmark']
        city = request.POST['city']
        district = request.POST['district']
        state = request.POST['state']
        country = request.POST['country']
        pincode = request.POST['pincode']
        
        #checking null values.
        if full_name.strip() == '' or house_name.strip() == '' or city.strip() == '' or district.strip() == '' or state.strip() == '' or country.strip() == '':
            messages.error(request, 'Some fields are missing.')
            return redirect('add_address')
        
        #creating new address.
        address = Address.objects.create(
            full_name=full_name,
            contact_number=contact_number,
            house_name=house_name,
            landmark=landmark,
            city=city,
            district=district,
            state=state,
            country=country,
            pincode=pincode,
            user=user,
        )
        messages.success(request,'Address has been added successfully.')
        return redirect('address')
        
    return render(request,'account/add_address.html') 


#To add address from checkout page.
@login_required(login_url='user_login')
def add_order_address(request):
    user = request.user
    if request.method == 'POST':
        full_name = request.POST['full_name']
        contact_number = request.POST['contact_number']
        house_name = request.POST['house_name']
        landmark = request.POST['landmark']
        city = request.POST['city']
        district = request.POST['district']
        state = request.POST['state']
        country = request.POST['country']
        pincode = request.POST['pincode']
        
        #checking null values.
        if full_name.strip() == '' or house_name.strip() == '' or city.strip() == '' or district.strip() == '' or state.strip() == '' or country.strip() == '':
            messages.error(request, 'Some fields are missing.')
            return redirect('add_order_address')
        
        #creating new address.
        address = Address.objects.create(
            full_name=full_name,
            contact_number=contact_number,
            house_name=house_name,
            landmark=landmark,
            city=city,
            district=district,
            state=state,
            country=country,
            pincode=pincode,
            user=user,
        )
        messages.success(request,'Address has been added successfully.')
        return redirect('checkout')
        
    return render(request,'account/add_order_address.html') 



@login_required(login_url='user_login')
def edit_address(request,address_id):

    user = request.user
    address = get_object_or_404(Address, id=address_id, user=user)

    if request.method == 'POST':    
        full_name = request.POST['full_name']
        contact_number = request.POST['contact_number']
        house_name = request.POST['house_name']
        landmark = request.POST['landmark']
        city = request.POST['city']
        district = request.POST['district']
        state = request.POST['state']
        country = request.POST['country']
        pincode = request.POST['pincode']


        #checking null values.
        if full_name.strip() == '' or house_name.strip() == '' or city.strip() == '' or district.strip() == '' or state.strip() == '' or country.strip() == '':
            # return HttpResponse('<div class="alert alert-danger alert-dismissible fade show" role="alert">Some fields are missing.</div>')
            messages.error(request,"Some fields are blank.")
            return redirect('edit_address')
        

        #updating address fields.
        address.full_name = full_name
        address.contact_number = contact_number
        address.house_name = house_name
        address.landmark = landmark
        address.city = city
        address.district = district
        address.state = state
        address.country = country
        address.pincode = pincode
        address.save()

        messages.success(request,"address edited successfully.")
        return redirect('address')
        
    return render(request,'account/edit_address.html',{'address':address})  
  
   

@login_required(login_url='user_login')
def delete_address(request,address_id):
    Address.objects.get(id=address_id).delete()
    messages.warning(request,'Address has been removed successfully.')
    return redirect('address')



@login_required(login_url='user_login')
def change_password(request):
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        # Verify if the old password is correct
        if not request.user.check_password(old_password):
            return HttpResponse('<div class="alert alert-danger alert-dismissible fade show" role="alert">Old password is not correct.</div>')  
    
        # Check if the new password and confirm password match
        if new_password != confirm_password:
            return HttpResponse('<div class="alert alert-danger" role="alert">Passwords dont match.</div>')
           
        
        # Update the user's password
        user = request.user
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user) 
        
        success_message = '<div class="alert alert-success" role="alert">Password changed successfully.</div>'

        # Create the response with success message and refresh instructions
        response = HttpResponse(success_message)
      
        return response


#userside
@login_required(login_url='user_login')
def orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request,'account/orders.html',{'orders':orders})  


#userside
@login_required(login_url='user_login')
def cancel_user_order(request,order_id):
    order = get_object_or_404(Order, id=order_id)

    # Update the order status to "Cancelled"
    order.status = 'Cancelled'
    order.refund_on_cancel()
    order.save()
    
    # Increase the product stock for each order item
    order_items = order.orderitem_set.all()
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity
        product.save()

    messages.warning(request,'Order has been cancelled successfully.')

    return redirect('orders') 


def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)
    context = {
        'order_items':order_items,
        'order':order
    }
    return render(request,'account/order_details.html',context)


def return_order_item(request,order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    return_item = ReturnItem()
    return_item.order_item = order_item
    return_item.refund_on_return()
    return_item.save()

    order_item.return_item = return_item
    order_item.is_returned = True
    order_item.save()
    
    order_id = order_item.order.id
    return redirect('order_details', order_id=order_id)



def generate_invoice_pdf(order):
    # Render the invoice template to a string
    invoice_html = render_to_string('account/invoice_template.html', {'order': order})

    # Create a temporary file path to save the PDF
    temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_invoice.pdf')

    # Generate the PDF using xhtml2pdf
    with open(temp_file_path, 'w+b') as file:
        pisa.CreatePDF(invoice_html, dest=file)

    return temp_file_path


def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    invoice_path = generate_invoice_pdf(order)

    if invoice_path:
        # Open the generated PDF file in binary mode
        with open(invoice_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="RR-order-invoice-{order_id}.pdf"'

        # Delete the temporary invoice file
        os.remove(invoice_path)

        return response

    return HttpResponse('Failed to generate the invoice', status=500)



    
      

   