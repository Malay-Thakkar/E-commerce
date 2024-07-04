from api.models import ProductModel
from customer.models import CustomUser

class Wishlist():
    #constructor callfor session id create if not exists
    def __init__(self, request):
        self.session = request.session
        self.request = request
        # get current session key
        wishlist = self.session.get('wishlist')
        # if no session key, create new user
        if 'wishlist' not in request.session:
            wishlist = self.session['wishlist'] = {}
        # Assign wishlist to self.wishlist
        self.wishlist = wishlist
    
    #on login add product in wishlist from database
    def db_add_wishlist(self, product):
        product_id = str(product)
        #if product id exits in wishlist then do nothing else add product and quantity
        if product_id in self.wishlist:
            pass
        else:
            self.wishlist[product_id] = {}
        self.session.modified = True
        
        #for login user to store in db 
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            likeproduct = str(self.wishlist)
            likeproduct = likeproduct.replace("\'","\"")
            current_user.update(old_wishlist=likeproduct) 
     
    #add product in cart         
    def add(self, product):
        product_id = str(product.product_id)
        
        #for session
        if product_id in self.wishlist:
            pass
        else:
            self.wishlist[product_id] = {'name': product.name, 'price': product.price}
        self.session.modified = True
        
        #for login user to store in db 
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            likeproduct = str(self.wishlist)
            likeproduct = likeproduct.replace("\'","\"")
            current_user.update(old_wishlist=likeproduct)

    #get total no of items in wishlist
    def __len__(self):
        return len(self.wishlist)

    # delete single products in wishlist
    def delete(self, product_id):
        if str(product_id) in self.wishlist:
            del self.wishlist[str(product_id)]
            self.session.modified = True
        if self.request.user.is_authenticated:
            current_user = CustomUser.objects.filter(id = self.request.user.id)
            likeproduct = str(self.wishlist)
            likeproduct = likeproduct.replace("\'","\"")
            current_user.update(old_wishlist=likeproduct)
     
    #get products from wishlist   
    def get_wishlist_product(self):
        wishlist_product_ids = list(self.wishlist.keys())
        products = ProductModel.objects.filter(product_id__in=wishlist_product_ids)
        return products
    