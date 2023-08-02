from django.shortcuts import render
from orders.models import Order,OrderItem
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime
import csv
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import login_required


@login_required(login_url='user_login')
def order_management(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    orders = Order.objects.all().order_by('-created_at')
    
    return render(request,'adminside_order/order_list.html',{'orders': orders} )


#adminside
@login_required(login_url='user_login')
def cancel_order(request,order_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    order = get_object_or_404(Order, id=order_id)

    # Update the order status to "Cancelled"
    order.status = 'Cancelled'
    order.save()

    # Increase the product stock for each order item
    order_items = order.orderitem_set.all()
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity
        product.save()

    messages.warning(request,'Order has been cancelled successfully.')

    return redirect('order_management')


@login_required(login_url='user_login')
def update_order_status(request, order_id):

    if not request.user.is_superuser:
        return redirect('index')
    
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        order.status = new_status
        order.save()
        messages.warning(request,'Order status has been changed successfully.')

    return redirect('order_management')

@login_required(login_url='user_login')
def sales_report(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    orders = Order.objects.all().order_by('-created_at')[:10] # Latest orders first

    # Get the start_date and end_date from the request's GET parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Parse the date strings to datetime objects
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        start_date = None

    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        end_date = None

    # Filter orders based on date range if start_date and end_date are provided
    if start_date and end_date:
        orders = Order.objects.filter(created_at__range=[start_date, end_date])
        
                

    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={
        'start_date': start_date_str,
        'end_date': end_date_str,
        'page_obj': page_obj,
    }
    
    return render(request,'adminside_order/sales_report.html',context)


@login_required(login_url='user_login')
def download_sales_report_csv(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Perform date filtering on orders using start_date and end_date
    orders = Order.objects.all()
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        orders = orders.filter(created_at__range=[start_date, end_date])

    # Create CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    writer = csv.writer(response)

    # Write CSV header
    writer.writerow(['Order ID', 'Payment Mode', 'Amount', 'Status', 'Ordered Date'])
    
    # Write CSV data rows
    for order in orders:
        writer.writerow([order.id, order.payment_mode, order.total_price, order.status, order.created_at])

    return response


@login_required(login_url='user_login')
def download_sales_report(request):

    if not request.user.is_superuser:
        return redirect('index')
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Perform date filtering on orders using start_date and end_date
    orders = Order.objects.all()
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        orders = orders.filter(created_at__range=[start_date, end_date])

    # Render the sales report template with the filtered orders
    template = get_template('adminside_order/sales_report_pdf.html')
    context = {'orders': orders}
    html = template.render(context)

    # Create a PDF file from the HTML content
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response, link_callback=fetch_resources)
    if not pdf.err:
        response = HttpResponse(response.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        return response

    return HttpResponse("Error generating PDF", status=500)

def fetch_resources(uri, rel):
    # Function to fetch external resources (e.g., CSS, images) for PDF generation
    # In this example, we assume that there are no external resources
    return uri