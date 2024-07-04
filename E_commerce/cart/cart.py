from api.models import ProductModel
from customer.models import CustomUser

class Cart():
    #constructor callfor session id create if not exists
    def __init__(self, request):
        self.session = request.session
        self.request = request
        # get current session key
        cart = self.session.get('session_key')
        # if no session key, create new user
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        # Assign cart to self.cart
        self.cart = cart

    #on login add product in cart from database
    def db_add(self, product,quantity):
        product_id = str(product)
        product_qty = str(quantity)
        
        #if product id exits in cart then do nothing else add product and quantity
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)
        self.session.modified = True 
        
        #for login user to store in db 
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'","\"")     
            current_user.update(old_cart=carty)
        
    #add product in cart    
    def add(self, product,quantity):
        product_id = str(product.product_id)
        product_qty = str(quantity)
        
        #for session
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)
        self.session.modified = True 
        
        #for login user to store in db 
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart=carty)
            
    #get total no of items in cart
    def __len__(self):
        return len(self.cart)
    
    #get products from cart
    def get_cart_product(self):
        cart_product_ids =list(self.cart.keys())
        products = ProductModel.objects.filter(product_id__in = cart_product_ids)
        return products
    
    #get product quntity from cart
    def get_quantity(self):
        quantity=self.cart
        return quantity
    
    #update product in cart
    def update(self,product,quantity):
        product_id = str(product)
        product_qty = int(quantity)
        
        #for session 
        ourcart = self.cart
        ourcart[product_id] = product_qty
        self.session.modified = True 
        
        #for login user to store in db 
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart=carty)
        things = self.cart
        return things
    
    # delete single products in cart 
    def delete(self,product):
        product_id = str(product)
        
        #for session
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
        
        #for login user to store in db 
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            current_user.update(old_cart=carty)
       
    #delete all product in cart     
    def delete_all(self):
        #for session 
        self.cart.clear()
        self.session.modified = True

        # For logged-in users to update the database
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id=self.request.user.id)
            current_user.update(old_cart="{}")  # Empty cart string representation
        

    #calculate total price
    def cart_total(self):
        cartitems = self.cart
        total = 0
        for key, value in cartitems.items():
            key = int(key)
            prod = ProductModel.objects.filter(product_id = key).values().first()
            if prod is not None:
                total += (prod['price'] * value)
            else:
                print(f"Product with ID {key} not found.")
        return total
        
    #calculate total with gst  
    def cart_gsttotal(self):
        cartitems = self.cart
        total = 0
        gsttotal=0
        for key, value in cartitems.items():
            key = int(key)
            prod = ProductModel.objects.filter(product_id = key).values().first()
            if prod is not None:
                total += (prod['price'] * value)
            else:
                print(f"Product with ID {key} not found.")
        gsttotal=((total*18)/100)+total
        return gsttotal