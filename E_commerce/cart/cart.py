import json
from api.models import ProductModel
from customer.models import CustomUser

class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request

        # --- THIS IS THE CRITICAL FIX ---
        # Check if the user is logged in
        if self.request.user.is_authenticated:
            # If logged in, try to load the cart from the database
            try:
                # user.old_cart is a string like '{"12": 1, "34": 2}'
                cart_data = self.request.user.old_cart
                if cart_data:
                    # json.loads() safely converts the string back to a dictionary
                    self.cart = json.loads(cart_data)
                else:
                    # If their db cart is empty, start a new one
                    self.cart = {}
            except (json.JSONDecodeError, TypeError):
                # If the data is corrupt, start with an empty cart
                self.cart = {}
        else:
            # For anonymous users, use the session as before
            self.cart = self.session.get('cart', {})
            self.session['cart'] = self.cart

    def _save(self):
        """A central method to save the cart to session and database."""
        # Save to session for all users
        self.session['cart'] = self.cart
        self.session.modified = True
        
        # If the user is logged in, also save to the database
        if self.request.user.is_authenticated:
            # json.dumps() safely converts the dictionary to a string
            current_user = CustomUser.objects.filter(id=self.request.user.id)
            current_user.update(old_cart=json.dumps(self.cart))

    def add(self, product, quantity):
        product_id = str(product.product_id)
        
        if product_id in self.cart:
            # If product exists, you might want to increase quantity instead of doing nothing
            # self.cart[product_id] += int(quantity)
            pass 
        else:
            self.cart[product_id] = int(quantity)
        
        self._save() # Call the central save method

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        
        self.cart[product_id] = product_qty
        self._save() # Call the central save method

    def delete(self, product):
        product_id = str(product)
        
        if product_id in self.cart:
            del self.cart[product_id]
        
        self._save() # Call the central save method

    # --- No changes needed for the methods below ---
    
    def __len__(self):
        return len(self.cart)
    
    def get_cart_product(self):
        cart_product_ids = list(self.cart.keys())
        products = ProductModel.objects.filter(product_id__in=cart_product_ids)
        return products
    
    def get_quantity(self):
        return self.cart

    def cart_total(self):
        # This method is still very slow but will work
        total = 0
        for key, value in self.cart.items():
            try:
                prod = ProductModel.objects.get(product_id=int(key))
                total += (prod.price * value)
            except ProductModel.DoesNotExist:
                continue
        return total
        
    def cart_gsttotal(self):
        total = self.cart_total()
        return ((total * 18) / 100) + total