from . import views
from django.urls import path, include

urlpatterns = [
    path('payment_success/', views.payment_success, name='payment_success'),        #Payment_success page
    path('payment_failed/', views.payment_failed, name='payment_failed'),           #Payment_Failed page
    path('checkout/', views.checkout, name='checkout'),                             #Payment_Checkout page
    path('billing_info/', views.billing_info, name='billing_info'),                 #Billing info page
    path('process_order/', views.process_order, name='process_order'),              #Process order page page
    path('shipped_dash/', views.shipped_dash, name='shipped_dash'),                 #Shipped_admin page 
    path('not_shipped_dash/', views.not_shipped_dash, name='not_shipped_dash'),     #not_Shipped_admin page
    path('orders/<int:pk>/', views.orders, name='orders'),                          #Order page
    path('paypal/', include("paypal.standard.ipn.urls")),                           #Paypal ipns page page
    path('payment-complete/', views.payment_complete, name='payment_complete'),     #Payment complete page
]
