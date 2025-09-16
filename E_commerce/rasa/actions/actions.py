import requests
from typing import Any, Text, Dict, List, TypedDict

# Rasa Imports
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# --- CONFIGURATION ---
API_BASE_URL = "http://web:8000/api/"

# --- HELPER FUNCTIONS ---
def get_auth_headers(tracker: Tracker) -> Dict[Text, Any] | None:
    """Extracts JWT token from tracker and prepares auth headers."""
    token = tracker.latest_message.get("metadata", {}).get("token")
    if not token:
        print("ACTION_SERVER_LOG: WARNING: Auth token not found in Rasa tracker.")
        return None
    return {"Authorization": f"Bearer {token}"}

def find_product_id(product_name: str, headers: dict) -> int | None:
    """Helper to find a product's ID from its name via Elasticsearch API search."""
    search_url = f"{API_BASE_URL}product/search/"
    try:
        response = requests.get(search_url, params={"search": product_name}, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get('status') == 'success' and result.get('products'):
            # Return the first (most relevant) product's ID
            return result['products'][0].get('product_id')
    except requests.exceptions.RequestException as e:
        print(f"ACTION_SERVER_LOG: Error finding product '{product_name}': {e}")
    return None

def handle_api_error(dispatcher: CollectingDispatcher, action_name: str, error: requests.exceptions.RequestException):
    """A centralized function to handle API errors gracefully."""
    print(f"--- API Call Failed: {action_name} ---")
    if error.response is not None:
        print(f"URL: {error.request.url}")
        print(f"Status Code: {error.response.status_code}")
        print(f"Response Body: {error.response.text}")
    else:
        print(f"Error: Could not connect to the server. Is the 'web' service running and healthy?")
    print(f"Full Exception: {error}")
    
    # Return user-friendly error message
    if hasattr(error, 'response') and error.response is not None:
        if error.response.status_code == 401:
            dispatcher.utter_message(text="Please log in to use this feature.")
        elif error.response.status_code == 404:
            dispatcher.utter_message(text="The requested item was not found.")
        elif error.response.status_code == 503:
            dispatcher.utter_message(text="Search service is temporarily unavailable. Please try again later.")
        else:
            dispatcher.utter_message(text="Sorry, something went wrong. Please try again later.")
    else:
        dispatcher.utter_message(text="Sorry, I'm having connection issues. Please try again in a moment.")

# --- CORE CHATBOT ACTIONS ---

class ActionSearchProduct(Action):
    def name(self) -> Text: 
        return "action_search_product"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        product_name = next(tracker.get_latest_entity_values("product_name"), None)
        
        if not product_name:
            dispatcher.utter_message(text="What product are you looking for?")
            return []
        
        # Use the new Elasticsearch-powered search API
        search_url = f"{API_BASE_URL}product/search/"
        try:
            response = requests.get(search_url, params={"search": product_name}, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'success' and result.get('products'):
                products = result['products']
                total_hits = result.get('total_hits', len(products))
                
                if len(products) == 1:
                    # Single product found
                    p = products[0]
                    message = f"I found this product: **{p.get('name')}**\n"
                    message += f"💰 Price: ₹{p.get('price')}\n"
                    if p.get('unit'):
                        message += f"📦 Unit: {p.get('unit')}\n"
                    if p.get('stock') is not None:
                        stock_status = "✅ In Stock" if p.get('stock') > 0 else "❌ Out of Stock"
                        message += f"📊 Status: {stock_status}\n"
                    if p.get('category') and p.get('category').get('name'):
                        message += f"🏷️ Category: {p.get('category').get('name')}\n"
                    
                    dispatcher.utter_message(text=message)
                    
                elif len(products) <= 5:
                    # Multiple products found (up to 5)
                    message = f"I found {len(products)} products matching '{product_name}':\n\n"
                    for i, p in enumerate(products, 1):
                        message += f"**{i}. {p.get('name')}**\n"
                        message += f"   💰 ₹{p.get('price')}"
                        if p.get('unit'):
                            message += f" per {p.get('unit')}"
                        message += "\n"
                        if p.get('category') and p.get('category').get('name'):
                            message += f"   🏷️ {p.get('category').get('name')}\n"
                        message += "\n"
                    
                    if total_hits > len(products):
                        message += f"... and {total_hits - len(products)} more results"
                    
                    dispatcher.utter_message(text=message)
                else:
                    # Many products found, show summary
                    message = f"I found {total_hits} products matching '{product_name}'. Here are the top 5:\n\n"
                    for i, p in enumerate(products[:5], 1):
                        message += f"**{i}. {p.get('name')}** - ₹{p.get('price')}\n"
                    
                    message += f"\n... and {total_hits - 5} more results. Try being more specific to narrow down the search."
                    dispatcher.utter_message(text=message)
                
                return [SlotSet("product_name", product_name)]
                
            else:
                error_msg = result.get('message', f"Sorry, I couldn't find any products matching '{product_name}'.")
                dispatcher.utter_message(text=error_msg)
                
        except requests.exceptions.RequestException as e:
            handle_api_error(dispatcher, self.name(), e)
        return []

class ActionAddToCart(Action):
    def name(self) -> Text: 
        return "action_add_to_cart"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        if not headers:
            dispatcher.utter_message(text="Please log in to add items to your cart.")
            return []
        
        product_name = next(tracker.get_latest_entity_values("product_name"), tracker.get_slot("product_name"))
        quantity = next(tracker.get_latest_entity_values("number"), 1)
        
        if not product_name:
            dispatcher.utter_message(text="Please tell me which product you'd like to add to your cart.")
            return []
        
        # Find product ID using Elasticsearch
        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a product named '{product_name}'. Try searching for products first to see what's available.")
            return []

        # Add to cart via API
        api_url = f"{API_BASE_URL}chatbot/cart/add/"
        payload = {
            "product_id": product_id,
            "product_qty": int(quantity) if isinstance(quantity, (int, str)) else 1
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'success':
                message = result.get('message', f"Added {product_name} to your cart!")
                cart_qty = result.get('cart_quantity')
                if cart_qty:
                    message += f" You now have {cart_qty} items in your cart."
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text=result.get('error', 'Failed to add item to cart.'))
                
        except requests.exceptions.RequestException as e:
            handle_api_error(dispatcher, self.name(), e)
        return []

class ActionViewCart(Action):
    def name(self) -> Text: 
        return "action_view_cart"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        if not headers:
            dispatcher.utter_message(text="Please log in to view your cart.")
            return []

        api_url = f"{API_BASE_URL}chatbot/cart/summary"
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            cart_data = response.json()
            
            if cart_data.get('status') == 'success' and cart_data.get('products'):
                products = cart_data['products']
                message = f"🛒 **Your Shopping Cart** ({len(products)} items):\n\n"
                
                for item in products:
                    message += f"• **{item['name']}**\n"
                    message += f"  📦 Quantity: {item['quantity']}\n"
                    message += f"  💰 Price: ₹{item['price']} each\n"
                    if 'total_price' in item:
                        message += f"  💵 Total: ₹{item['total_price']}\n"
                    message += "\n"
                
                message += f"💳 **Subtotal:** ₹{cart_data['total']}\n"
                message += f"🏛️ **Total (with GST):** ₹{cart_data['gst_total']}"
                
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="🛒 Your shopping cart is empty. Would you like to search for some products?")
                
        except requests.exceptions.RequestException as e:
            handle_api_error(dispatcher, self.name(), e)
        return []

class ActionRemoveFromCart(Action):
    def name(self) -> Text: 
        return "action_remove_from_cart"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        if not headers:
            dispatcher.utter_message(text="Please log in to modify your cart.")
            return []
        
        product_name = next(tracker.get_latest_entity_values("product_name"), tracker.get_slot("product_name"))
        
        if not product_name:
            dispatcher.utter_message(text="Please tell me which product you'd like to remove from your cart.")
            return []
        
        # Find product ID using Elasticsearch
        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a product named '{product_name}' to remove from your cart.")
            return []

        # Remove from cart via API
        api_url = f"{API_BASE_URL}chatbot/cart/delete/"
        payload = {"product_id": product_id}
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'success':
                dispatcher.utter_message(text=result.get('message', f"Removed {product_name} from your cart!"))
            else:
                dispatcher.utter_message(text=result.get('error', 'Failed to remove item from cart.'))
                
        except requests.exceptions.RequestException as e:
            handle_api_error(dispatcher, self.name(), e)
        return []

class ActionUpdateCartQuantity(Action):
    def name(self) -> Text: 
        return "action_update_cart_quantity"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        if not headers:
            dispatcher.utter_message(text="Please log in to modify your cart.")
            return []
        
        product_name = next(tracker.get_latest_entity_values("product_name"), tracker.get_slot("product_name"))
        quantity = next(tracker.get_latest_entity_values("number"), None)
        
        if not product_name or not quantity:
            dispatcher.utter_message(text="Please tell me which product and the new quantity you'd like.")
            return []
        
        # Find product ID using Elasticsearch
        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a product named '{product_name}' in your cart.")
            return []

        # Update cart via API
        api_url = f"{API_BASE_URL}chatbot/cart/update/"
        payload = {
            "product_id": product_id,
            "product_qty": int(quantity)
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'success':
                dispatcher.utter_message(text=result.get('message', f"Updated {product_name} quantity to {quantity}!"))
            else:
                dispatcher.utter_message(text=result.get('error', 'Failed to update cart.'))
                
        except requests.exceptions.RequestException as e:
            handle_api_error(dispatcher, self.name(), e)
        return []

class ActionAddToWishlist(Action):
    def name(self) -> Text: 
        return "action_add_to_wishlist"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        if not headers:
            dispatcher.utter_message(text="Please log in to add items to your wishlist.")
            return []
        
        product_name = next(tracker.get_latest_entity_values("product_name"), tracker.get_slot("product_name"))
        
        if not product_name:
            dispatcher.utter_message(text="Please tell me which product you'd like to add to your wishlist.")
            return []
        
        # Find product ID using Elasticsearch
        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a product named '{product_name}'. Try searching for products first.")
            return []

        # Add to wishlist via API
        api_url = f"{API_BASE_URL}chatbot/wishlist/add/"
        payload = {"product_id": product_id}
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'success':
                dispatcher.utter_message(text=result.get('message', f"Added {product_name} to your wishlist!"))
            else:
                dispatcher.utter_message(text=result.get('error', 'Failed to add item to wishlist.'))
                
        except requests.exceptions.RequestException as e:
            handle_api_error(dispatcher, self.name(), e)
        return []

class ActionViewPastOrders(Action):
    def name(self) -> Text: 
        return "action_view_past_orders"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        dispatcher.utter_message(text="📋 Order history functionality is coming soon! I can help you with your current cart and wishlist for now.")
        return []