import json
from api.models import ProductModel
from customer.models import CustomUser

class Wishlist():
    def __init__(self, request):
        self.session = request.session
        self.request = request

        # FIX: Loads from the database for logged-in users, just like the Cart
        if self.request.user.is_authenticated:
            try:
                wishlist_data = self.request.user.old_wishlist
                # Safely convert the string back to a dictionary
                self.wishlist = json.loads(wishlist_data) if wishlist_data else {}
            except (json.JSONDecodeError, TypeError):
                self.wishlist = {} # If data is corrupt, start fresh
        else:
            # For anonymous users, use the session, just like the Cart
            self.wishlist = self.session.get('wishlist', {})
            self.session['wishlist'] = self.wishlist

    def _save(self):
        """A central method to save, identical to the Cart's save method."""
        self.session['wishlist'] = self.wishlist
        self.session.modified = True
        
        if self.request.user.is_authenticated:
            # Safely convert the dictionary to a JSON string before saving
            current_user = CustomUser.objects.filter(id=self.request.user.id)
            current_user.update(old_wishlist=json.dumps(self.wishlist))

    def add(self, product):
        """Adds a product to the wishlist dictionary."""
        product_id = str(product.product_id)
        
        # We use '1' as a placeholder value, similar to quantity in the cart
        if product_id not in self.wishlist:
            self.wishlist[product_id] = 1 
            self._save() # Call the central save method

    def delete(self, product_id):
        """Removes a product from the wishlist dictionary."""
        product_id_str = str(product_id)
        if product_id_str in self.wishlist:
            del self.wishlist[product_id_str]
            self._save() # Call the central save method
    
    def __len__(self):
        """Returns the total number of items in the wishlist."""
        return len(self.wishlist)
    
    def get_wishlist_product(self):
        """Returns product objects from the keys of the wishlist dictionary."""
        # Get the product IDs from the dictionary keys
        wishlist_product_ids = self.wishlist.keys()
        return ProductModel.objects.filter(product_id__in=wishlist_product_ids)