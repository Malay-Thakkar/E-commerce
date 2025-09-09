import requests
from typing import Any, Text, Dict, List, TypedDict
import logging

# Rasa Imports
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# LangChain / LangGraph Imports
from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, ToolMessage

# --- CONFIGURATION ---
API_BASE_URL = "http://172.18.0.6:8000/api/"
logger = logging.getLogger(__name__)

# --- HELPER FUNCTIONS ---
def get_auth_headers(tracker: Tracker) -> Dict[Text, Any] | None:
    """Extract JWT token from tracker metadata."""
    token = tracker.latest_message.get("metadata", {}).get("token")
    if not token:
        logger.warning("Auth token not found in Rasa tracker.")
        return None
    return {"Authorization": f"Bearer {token}"}

def find_product_id(product_name: str, headers: dict) -> int | None:
    """Helper to find a product's ID from its name via API search."""
    search_url = API_BASE_URL + "product/"
    try:
        response = requests.get(search_url, params={"search": product_name}, headers=headers)
        response.raise_for_status()
        products = response.json()
        if products:
            return products[0].get('product_id')
    except requests.exceptions.RequestException as e:
        print(f"Error finding product '{product_name}': {e}")
    return None

# --- LANGGRAPH AGENT & TOOLS (For Complex Queries) ---
@tool
def search_product_by_name_agent(product_name: str) -> Dict[str, Any]:
    """A tool for the AI agent to search for a product by its name and get its details."""
    print(f"--- AGENT TOOL: Searching for product: {product_name} ---")
    # This is a placeholder and could be expanded to call the real API
    # and provide much more detailed information for the LLM to reason about.
    if "macbook" in product_name.lower():
        return {"id": "prod_123", "name": "Macbook Pro", "price": 1999.99, "category": "Laptops"}
    else:
        return {"error": "Product not found."}

class AgentState(TypedDict):
    messages: List[Any]

llm = ChatOllama(model="phi3:mini", base_url="http://ollama:11434")
tools = [search_product_by_name_agent]
tool_executor = ToolExecutor(tools)

def should_continue(state: AgentState):
    if not state['messages'][-1].tool_calls:
        return "end"
    return "continue"

def call_model(state: AgentState):
    response = llm.invoke(state['messages'])
    return {"messages": state['messages'] + [response]}

def call_tool(state: AgentState):
    last_message = state['messages'][-1]
    tool_outputs = []
    for tool_call in last_message.tool_calls:
        tool_output = tool_executor.invoke(tool_call)
        tool_outputs.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call['id']))
    return {"messages": state['messages'] + tool_outputs}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge('action', 'agent')
agent_graph = workflow.compile()

# --- RASA ACTIONS ---

class ActionTriggerResearchAgent(Action):
    def name(self) -> Text: return "action_trigger_research_agent"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        user_query = tracker.latest_message['text']
        dispatcher.utter_message(text="Let me research that for you...")
        try:
            inputs = {"messages": [HumanMessage(content=user_query)]}
            final_state = agent_graph.invoke(inputs)
            llm_response = final_state['messages'][-1].content
            dispatcher.utter_message(text=llm_response)
        except Exception as e:
            print(f"Error running LangGraph agent: {e}")
            dispatcher.utter_message(text="Sorry, I ran into an issue processing your complex request.")
        return []

class ActionSearchProduct(Action):
    def name(self) -> Text:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        product_name = next(tracker.get_latest_entity_values("product_name"), None)
        
        if not product_name:
            dispatcher.utter_message(text="What product are you looking for?")
            return []
        
        search_url = f"{API_BASE_URL}product/"
        
        try:
            response = requests.get(
                search_url, 
                params={"search": product_name}, 
                headers=headers
            )
            response.raise_for_status()
            products = response.json()
            
            if products:
                message = f"I found these products matching '{product_name}':\n"
                for p in products:
                    message += f"- {p.get('name')} (${p.get('price')})\n"
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(
                    text=f"Sorry, I couldn't find any products matching '{product_name}'."
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error: {e}")
            dispatcher.utter_message(
                text="Sorry, I'm having trouble searching our inventory right now."
            )
        
        return [SlotSet("product_name", product_name)]

class ActionAddToCart(Action):
    def name(self) -> Text: return "action_add_to_cart"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        product_name = next(tracker.get_latest_entity_values("product_name"), tracker.get_slot("product_name"))
        if not product_name:
            dispatcher.utter_message(response="utter_ask_product_for_cart")
            return []
        print("\n\n\n\n\n\n\tsfdfsdfsdf",product_name)
        product_id = find_product_id(product_name, headers)
        print("\n\n\n\n\n\n\tsfdfsdfsdf",product_id)
        product_id = 4

        if not product_id:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a product named '{product_name}'.")
            return []

        api_url = API_BASE_URL + "chatbot/cart/add/"
        print(f"Adding product ID {product_id} to cart via {api_url}")
        
        payload = {"product_id": product_id}
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            dispatcher.utter_message(text=f"Done! I've added {product_name} to your cart.")
        except requests.exceptions.RequestException as e:
            print(f"API Error (Add to Cart): {e.response.text if e.response else e}")
            dispatcher.utter_message(text=f"Sorry, I couldn't add {product_name} to your cart right now.")
        return []

class ActionAddToWishlist(Action):
    def name(self) -> Text: return "action_add_to_wishlist"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        product_name = next(tracker.get_latest_entity_values("product_name"), tracker.get_slot("product_name"))
        if not product_name:
            dispatcher.utter_message(text="What product would you like to add to your wishlist?")
            return []
        
        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"Sorry, I couldn't find a product named '{product_name}'.")
            return []

        api_url = API_BASE_URL + "chatbot/wishlist/add/"
        payload = {"product_id": product_id}
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            dispatcher.utter_message(text=f"Okay, I've added {product_name} to your wishlist.")
        except requests.exceptions.RequestException as e:
            print(f"API Error (Add to Wishlist): {e.response.text if e.response else e}")
            dispatcher.utter_message(text=f"Sorry, I couldn't add {product_name} to your wishlist right now.")
        return []

class ActionRemoveFromCart(Action):
    def name(self) -> Text: return "action_remove_from_cart"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        product_name = next(tracker.get_latest_entity_values("product_name"), None)
        if not product_name:
            dispatcher.utter_message(response="utter_ask_product_for_removal")
            return []

        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"I couldn't find '{product_name}' in your cart.")
            return []

        api_url = API_BASE_URL + "chatbot/cart/delete/"
        payload = {"product_id": product_id}
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            dispatcher.utter_message(text=f"Okay, I've removed {product_name} from your cart.")
        except requests.exceptions.RequestException as e:
            print(f"API Error (Remove from Cart): {e.response.text if e.response else e}")
            dispatcher.utter_message(text=f"Sorry, I had trouble removing {product_name} from your cart.")
        return []

class ActionUpdateCartQuantity(Action):
    def name(self) -> Text: return "action_update_cart_quantity"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        product_name = next(tracker.get_latest_entity_values("product_name"), None)
        quantity = next(tracker.get_latest_entity_values("quantity"), None)
        if not product_name or not quantity:
            dispatcher.utter_message(response="utter_ask_product_for_update")
            return []

        product_id = find_product_id(product_name, headers)
        if not product_id:
            dispatcher.utter_message(text=f"I couldn't find '{product_name}' to update.")
            return []

        api_url = API_BASE_URL + "chatbot/cart/update/"
        payload = {"product_id": product_id, "quantity": int(quantity)}
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            dispatcher.utter_message(text=f"I've updated the quantity for {product_name} to {quantity}.")
        except requests.exceptions.RequestException as e:
            print(f"API Error (Update Cart): {e.response.text if e.response else e}")
            dispatcher.utter_message(text=f"Sorry, I couldn't update the quantity for {product_name}.")
        return []

class ActionViewCart(Action):
    def name(self) -> Text:
        return "action_view_cart"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        token = tracker.get_latest_input_channel()  # Or metadata["token"]

        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(
                url = "http://0.0.0.0:8000/api/chatbot/cart/summary/",
                headers=headers,
                timeout=10
            )
            print("\n\n\n\n\n\n\tsfdfsdfsdf",response)
            if response.status_code == 200:
                data = response.json()
                # Format response
                message = "Here is your cart:\n"
                for p in data['products']:
                    message += f"- {p['name']} x {p['quantity']} (${p['price']})\n"
                message += f"Total: ${data['total']} (+GST: ${data['gst_total']})"
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Sorry, I'm having trouble viewing your cart right now.")
        except Exception as e:
            print(f"Error in action_view_cart: {e}")
            dispatcher.utter_message(text="Sorry, I'm having trouble viewing your cart right now.")
        return []

        return []

class ActionViewPastOrders(Action):
    def name(self) -> Text: return "action_view_past_orders"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        headers = get_auth_headers(tracker)
        # NOTE: You will need to create a '/api/orders/' endpoint for this to work.
        # This is a placeholder until that endpoint is created.
        orders_url = API_BASE_URL + "orders/"
        dispatcher.utter_message(text="Sorry, the ability to view past orders is still under development.")
        return []

