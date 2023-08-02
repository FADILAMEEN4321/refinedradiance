from django.urls import path
from .views import *

urlpatterns = [  
    #order management.
    path('order_management',order_management, name='order_management'),
    path('cancel_order/<int:order_id>',cancel_order, name='cancel_order'),
    path('update_order_status/<int:order_id>',update_order_status, name='update_order_status'),
    
    #sales report.
    path('sales_report', sales_report, name='sales_report'),
    path('download_sales_report_csv', download_sales_report_csv, name='download_sales_report_csv'),
    path('download_sales_report', download_sales_report, name='download_sales_report'),
]
