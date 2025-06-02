from . import views
from django.urls import path, include
from .views import support_voice


#URLS for routing pages in the website 
urlpatterns = [
    path('',views.home, name = 'home'),                                       #home Urls
    path('about/',views.about, name = 'about'),                                 #about Urls
    path('login/',views.login_user, name = 'login'),                            #login Urls
    path('logout/',views.logout_user, name = 'logout'),                         #logout Urls
    path('register/',views.register_user, name = 'register'),                   #register Urls
    path('update_password/',views.update_password, name = 'update_password'),   #Update_passsword Urls
    path('update_user/',views.update_user, name = 'update_user'),               #Update_user Urls
    path('update_info/',views.update_info, name = 'update_info'),               #Update_info Urls
    path('product/<int:pk>',views.product, name = 'product'),                   #Product Urls
    path('category/<str:foo>',views.category, name = 'category'),               #Category Urls
    path('category_summary/',views.category_summary, name = 'category_summary'),#Summery Urls
    path('search/',views.search, name = 'search'),                              #Search Urls
    path('support/', views.support_page, name='support'),                       #Support Urls
    path('support-voice/', views.support_voice, name='support_voice'),
    
]