from . import views
from django.urls import path, include

urlpatterns = [
    path('',views.cart_summery,name = 'cart_summery'),              #cart summery page
    path('add/',views.cart_add,name = 'cart_add'),                  #adding product to cart page
    path('delete/',views.cart_delete,name = 'cart_delete'),         #delete cart page
    path('update/',views.cart_update,name = 'cart_update'),         #Update cart page
]