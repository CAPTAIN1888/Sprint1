from  store.models import Product ,Profile


#Cart calss to for all backend work related to cart
class Cart():
    def __init__(self,request):
        self.session = request.session

        self.request = request

        cart = self.session.get('session_key')

        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}


        self.cart = cart

#adding information to database
    def db_add(self,product,quantity):
        product_qty = str(quantity)
        product_id = str(product)
        if product_id in self.cart:
            pass
        else:

            #self.cart[product_id] = {'price':str(product.price)}
            self.cart[product_id] = int(product_qty)



        self.session.modified = True

        if self.request.user.is_authenticated:
            
            
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart = str(carty))

#
    def add(self,product,quantity):
        product_qty = str(quantity)
        product_id = str(product.id)
        if product_id in self.cart:
            pass
        else:

            #self.cart[product_id] = {'price':str(product.price)}
            self.cart[product_id] = int(product_qty)



        self.session.modified = True

        if self.request.user.is_authenticated:
            
            
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart = str(carty))

    def __len__(self):
        return len(self.cart)
    
#getting products anf filter out using filter
    def get_prods(self):
        products_ids = self.cart.keys()

        products = Product.objects.filter(id__in=products_ids)
        return products
    
#getting quantities of product
    def get_quants(self):
        quantities = self.cart
        return quantities
    
#Updating cart method
    def update(self,product,quantity):
        product_id = str(product)
        product_qty = int(quantity)

        ourcart = self.cart
        ourcart[product_id] = product_qty

        self.session.modified = True

        thing =self.cart


        if self.request.user.is_authenticated:
            
            
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart = str(carty))
        thing = self.cart
        return thing
    
#delete current cart after payment or before payment
    def delete(self,product):
        product_id = str(product)
        if  product_id in self.cart:
            del self.cart[product_id]
            

        self.session.modified =True


        if self.request.user.is_authenticated:
            
            
            current_user = Profile.objects.filter(user__id=self.request.user.id)

            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart = str(carty))


#Total cart information or product information into cart 
    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart

        total = 0
        for key ,value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total

