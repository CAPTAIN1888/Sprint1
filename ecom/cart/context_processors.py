from .cart import Cart

# create context proecessor fror all pages

def cart(request):
    return{'cart':Cart(request)}