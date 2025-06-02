from django.shortcuts import render ,redirect
from .models import Product,Category ,Profile
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm , UpdateUserForm ,ChangePasswordForm,  UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from django.http import HttpResponse ,HttpResponseBadRequest


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Searching method for search items according to description and name of product

def search(request):
    if request.method =="POST":
        searched = request.POST['searched']


        searched = Product.objects.filter(Q(name__icontains = searched) | Q(description__icontains = searched))

        if not searched :
            messages.success(request ,"That Product does not exist")
            return render(request ,"search.html",{'searched':searched})
        else:
            return render(request ,"search.html",{'searched':searched})
    else:
        return render(request ,"search.html",{})


# Update User profile information
def update_info(request):
    if request.user.is_authenticated: 
        #get shipping info of current user
        current_user,_ = Profile.objects.get_or_create(user=request.user)
        
        #getting shipping address of user
        shipping_user,_ = ShippingAddress.objects.get_or_create(user=request.user)        
        
        form = UserInfoForm(request.POST or None, instance = current_user)
        #get user shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        


        if form.is_valid() or shipping_form.is_valid():
            #original form
            form.save()
            shipping_form.save()

            #shipping_form.save()
            messages.success(request, "Your Info has been Updated")
            return redirect('home')
        return render(request,"update_info.html",{'form':form,'shipping_form':shipping_form})
    
    else:
        messages.success(request, "User Must be login to access this page")
        return redirect('home')


# To update password for user authentication

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user,request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,"your password is updated")
                login(request,current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.success(request,error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
        return render(request, "update_password.html", {'form':form})
    else:
        messages.success(request, "you must be logged in")
        return redirect('home')



#Update User name and other info

def update_user(request):
    if request.user.is_authenticated: 
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance = current_user)

        if user_form.is_valid():
            user_form.save()

            login(request,current_user)
            messages.success(request, "User has been Updated")
            return redirect('home')
        return render(request,"update_user.html",{'user_form':user_form})
    
    else:
        messages.success(request, "User Must be login to access this page")
        return redirect('home')



# rendering category page to user
def category_summary(request):
    categories = Category.objects.all()
    return render(request,'category_summary.html',{"categories":categories})


# Show items as per category to customer for easy traversing items to buy
def category(request, foo):
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {
            'products': products,
            'category': category
        })
    except Category.DoesNotExist:
        messages.error(request, "That category does not exist!!")
        return redirect('home')


# rendering product to user
def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html',{'product':product})




# rendering home page to user
def home(request):
    products = Product.objects.all()
    return render(request , 'home.html', {'products':products})


# rendering about page to user
def about(request):
        return render(request , 'about.html', {})

# Login -- verification and authentication for user
def login_user(request):
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request,username = username,password=password)
            if user is not None:
                    login(request,user)

                    current_user = Profile.objects.get(user__id=request.user.id)

                    saved_cart = current_user.old_cart

                    if saved_cart:
                        converted_cart = json.loads(saved_cart)
                        cart = Cart(request)

                        for key,value in converted_cart.items():
                            cart.db_add(product=key,quantity=value)
                
                    messages.success(request,("you have been logged in!!"))
                    return redirect('home')
            else:
                messages.success(request, ("There was an error, please try again..."))
                return redirect('login')


        else:
            return render(request , 'login.html', {})


# Logout page rendering method
def logout_user(request):
    logout(request)
    messages.success(request, ("you have been logged out!!"))
    return redirect('home')


# Getting info from user and register into database for access website
def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user

            user = authenticate(username=username,password=password)
            login(request , user)
            messages.success(request, ("Username Created - Fill other info!!"))
            return redirect('update_info')
        
        else:
            print(form.errors)
            messages.success(request, (form.errors))
            return redirect('register')
    else:
        return render(request , 'register.html',{'form':form})
    




# rendering support page method
def support_page(request):
    return render(request, 'support.html') 


# Support System for user help based on voice assistant 
@csrf_exempt
def support_voice(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query", "")
            query = query.lower()
            
            # conditions for reply as per clients query or any issue
            if "login" in query or "register" in query:
                reply = "  You need to Register to website and then login , if it doesn't work try checking validation for email and other fields"
                
            elif "shipping time" in query or "shipping details" in query:
                reply = "  Shipping takes 3 to 5 business days."
            
            elif "how to add product to cart" in query:
                reply = "  You can search the product you want add , view it , you will get and option for adding to cart ! Happy Shopping"

            elif "why delivery is late" in query:
                reply = "  Sorry for your inconvinience, we will help to resolve it as soon as we can, for more info you can call on this number 9876543210"


            else:
                reply = "Sorry, I didn't understand your question."

            return JsonResponse({"reply": reply})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponseBadRequest("This endpoint only accepts POST requests.")