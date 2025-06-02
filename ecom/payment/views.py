from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from store.models import Profile
from django.conf import settings
import datetime
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest


#Razorpay Credentials for payment gateway you add your own
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


"""
View to display and update order shipping status.
Accessible only to authenticated superusers.
"""

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)

# Update shipping status based on form submission
        if request.method == "POST":
            status = request.POST.get('shipping_status')
            now = datetime.datetime.now()
            if status == "true":
                order.shipped = True
                order.date_shipped = now
            else:
                order.shipped = False
            order.save()
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/orders.html", {"order": order, "items": items})
    else:
        messages.error(request, "Access Denied!")
        return redirect('home')


def not_shipped_dash(request):

    """
    Dashboard to show orders that are not yet shipped.
    Superusers can mark orders as shipped here.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.method == "POST":
            order_id = request.POST.get('num')
            order = Order.objects.get(id=order_id)
            order.shipped = True
            order.date_shipped = datetime.datetime.now()
            order.save()
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/not_shipped_dash.html", {"orders": orders})
    else:
        messages.error(request, "Access Denied!")
        return redirect('home')


def shipped_dash(request):

    """
    Dashboard to show orders that are already shipped.
    Superusers can mark orders as not shipped (reverse action).
    """


    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.method == "POST":
            order_id = request.POST.get('num')
            order = Order.objects.get(id=order_id)
            order.shipped = False
            order.save()
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/shipped_dash.html", {"orders": orders})
    else:
        messages.error(request, "Access Denied!")
        return redirect('home')


def checkout(request):

    """
    Display checkout page with cart details and shipping form.
    If the user is authenticated, pre-fill shipping form with their saved address.
    """
    cart = Cart(request)
    cart_products = cart.get_prods          #List Of products in cart
    quantities = cart.get_quants            #quantities fo the product
    totals = cart.cart_total()          

    if request.user.is_authenticated:
        shipping_user, _ = ShippingAddress.objects.get_or_create(user=request.user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
    else:
        shipping_form = ShippingForm(request.POST or None)

    context = {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form,
    }
    return render(request, "payment/checkout.html", context)


def billing_info(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = "%.2f" % float(cart.cart_total())
        total_in_paise = int(float(totals) * 100)

        # Save shipping info in session
        shipping_info = request.POST
        request.session['my_shipping'] = shipping_info

        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": total_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })

        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': total_in_paise,
            'currency': "INR",
            'totals': totals,
            'cart_products': cart_products,
            'quantities': quantities,
            'shipping_info': shipping_info,
            'billing_form': PaymentForm(),
        }
        return render(request, "payment/billing_info.html", context)
    else:
        messages.error(request, "Access Denied!")
        return redirect('home')


@csrf_exempt
def payment_success(request):

    """
    Callback endpoint Razorpay posts to after payment is complete.
    Verifies payment signature and finalizes order creation.
    """
    if request.method == "POST":
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
     # Verify payment authenticity via Razorpay SDK
        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'payment/payment_failed.html')

        # Payment verified, complete order creation process
        order = complete_order(request)
        if not order:
            return redirect('home')

        return render(request, 'payment/payment_success.html', {'order': order})

    elif request.method == "GET":
        return render(request, 'payment/payment_success.html')
    else:
        # Other HTTP methods are invalid
        return HttpResponseBadRequest("Invalid Request")

#payment Failed page to render
def payment_failed(request):
    return render(request, 'payment/payment_failed.html')


def complete_order(request):
    """
    Helper to create order and order items from session and cart after payment success.
    """
    cart = Cart(request)
    cart_products = cart.get_prods()  # Call the method to get the list of products
    quantities = cart.get_quants()    # Call the method to get the dict {product_id: quantity}
    totals = cart.cart_total()

    my_shipping = request.session.get('my_shipping')
    if not my_shipping:
        messages.error(request, "Shipping information missing. Please try again.")
        return None

    full_name = my_shipping.get('shipping_full_name', '')
    email = my_shipping.get('shipping_email', '')

    shipping_address = (
        f"{my_shipping.get('shipping_address1', '')}\n"
        f"{my_shipping.get('shipping_address2', '')}\n"
        f"{my_shipping.get('shipping_city', '')}\n"
        f"{my_shipping.get('shipping_state', '')}\n"
        f"{my_shipping.get('shipping_zipcode', '')}\n"
        f"{my_shipping.get('shipping_country', '')}"
    )

    amount_paid = totals

    if request.user.is_authenticated:
        user = request.user
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid,
            paid=True,
            shipped=False,
        )
        # Loop over products once, then get quantity from quantities dict
        for product in cart_products:
            qty = quantities.get(str(product.id)) or quantities.get(product.id) or 0
            if qty > 0:
                price = product.sale_price if product.is_sale else product.price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    user=user,
                    quantity=qty,
                    price=price
                )
        # Clear cart session key and old_cart in profile
        if "session_key" in request.session:
            del request.session["session_key"]
        Profile.objects.filter(user=user).update(old_cart="")

    else:
        # For anonymous users (no user attached to order)
        order = Order.objects.create(
            full_name=full_name,
            email=email,
            shipping_address=shipping_address,
            amount_paid=amount_paid,
            paid=True,
            shipped=False,
        )
        for product in cart_products:
            qty = quantities.get(str(product.id)) or quantities.get(product.id) or 0
            if qty > 0:
                price = product.sale_price if product.is_sale else product.price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=price
                )
        if "session_key" in request.session:
            del request.session["session_key"]

    # Clear cart items after order is complete
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True

    return order


# views.py
from django.shortcuts import render

def process_order(request):
    # your processing code here
    return render(request, 'some_template.html')

# payment/views.py

from django.shortcuts import render
from django.http import HttpResponse

def payment_complete(request):
    return HttpResponse("Payment completed successfully!")


