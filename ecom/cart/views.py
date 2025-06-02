from django.shortcuts import render ,get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages




# View to display the cart summary page with products, quantities, and totals
def cart_summery(request):

    cart = Cart(request)
    cart_products = cart.get_prods          # List of products in the cart
    quantities = cart.get_quants                # Corresponding quantities for each product
    totals = cart.cart_total()              # Total price of all products in the cart
    return render(request, "cart_summery.html",{"cart_products":cart_products, "quantities":quantities,"totals":totals})

def cart_add(request):
    cart = Cart(request)


  # Check if the request has the correct 'action' parameter
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

    # Get the product object or return 404 if not found
        product = get_object_or_404(Product,id=product_id)
        cart.add(product=product,quantity=product_qty)

        cart_quantity = cart.__len__()

 # Return a JSON response with the updated cart quantity
        #response = JsonResponse({'Product Name':product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.error(request, "Product added to cart!!")

        return response


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':

             # Remove the product from the cart by product ID   
        product_id = int(request.POST.get('product_id'))

        cart.delete(product=product_id)
        response = JsonResponse({'product':product_id})
        messages.error(request, "Item deleted from cart!!")

        return response



# View to update the quantity of a product in the cart via AJAX POST request
def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # Update the product quantity in the cart

        cart.update(product = product_id,quantity = product_qty)
        response = JsonResponse({'qty':product_qty})

        # Add a message to inform the user the cart was updated
        messages.error(request, "Your Cart Updated!!")

        return response
        #return redirect('cart_summery')