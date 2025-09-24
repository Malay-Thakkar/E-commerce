from django.shortcuts import render, get_object_or_404
from api.models import ProductModel
from django.http import JsonResponse
from .cart import Cart
from .wishlist import Wishlist
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    CartWishlistSerializer, 
    CartUpdateSerializer,
)
from api.serializers import(
    ProductSerializers,
    CategorySerializers
)
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


#cart page view 
def cart_summary(request):
    cart=Cart(request)
    cart_products =cart.get_cart_product()
    cart_quantity =cart.get_quantity()
    total = cart.cart_total()
    gsttotal = cart.cart_gsttotal()
    return render(request,'cart.html',{'cart_products':cart_products,'cart_quantity':cart_quantity,'total':total,'gsttotal':gsttotal})


#for add products in carts 
def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        #get from DB
        product = get_object_or_404(ProductModel,product_id=product_id)
        cart.add(product=product,quantity=product_qty)
        cart_quantity = len(cart)
        # cart_quantity = cart.__len__()
        response =JsonResponse({'cart_quantity':cart_quantity})
        messages.success(request,'successfully added Items')
        return response
    
#for delete products in cart
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        response = JsonResponse({'product_id':product_id})
        messages.success(request,'successfully deleted Items')
        return response

#for update products(quantity) in cart
def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action')=='post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart.update(product=product_id,quantity=product_qty)
        response = JsonResponse({'qty':product_qty})
        return response

#wishlist views:
def wishlist_summary(request):
    wishlist = Wishlist(request)
    wishlist_products = wishlist.get_wishlist_product()
    return render(request, 'wishlist.html', {'wishlist_products': wishlist_products})

#for add product in wishlist
def wishlist_add(request):
    wishlist = Wishlist(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product = get_object_or_404(ProductModel, product_id=product_id)
        wishlist.add(product=product)
        messages.success(request, 'Successfully added to wishlist')
        return JsonResponse({'success': True})

#for delete product in wishlist
def wishlist_delete(request):
    wishlist = Wishlist(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        wishlist.delete(product_id)
        messages.success(request, 'Successfully deleted from wishlist')
        return JsonResponse({'success': True})

#for rasa handel apis
class CartAddAPIView(APIView):
    """API endpoint for the chatbot to add items to the user's cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            product_id = int(request.data.get('product_id'))
            quantity = int(request.data.get('product_qty', 1))

            if not product_id:
                return Response(...)

            # FIX #2: Get the actual product object from the database
            product = get_object_or_404(ProductModel, product_id=product_id)
            
            cart = Cart(request)
            
            # FIX #1: Use the 'cart' object's own 'add' method correctly
            cart.add(product=product, quantity=quantity) 

            return Response({
                "status": "success",
                "message": f"Successfully added {product.name} to cart",
                # FIX #3: Calculate the cart quantity correctly
                "cart_quantity": len(cart), 
            }, status=status.HTTP_200_OK)
     
            
        except ProductModel.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {"error": "Invalid product ID or quantity"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while adding to cart"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WishlistAddAPIView(APIView):
    """API endpoint for the chatbot to add items to the user's wishlist."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            product_id = int(request.data.get('product_id'))

            if not product_id:
                return Response(...)

            # FIX #2: Get the actual product object from the database
            product = get_object_or_404(ProductModel, product_id=product_id)
            
            wishlist = Wishlist(request)
            
            # FIX #1: Use the 'cart' object's own 'add' method correctly
            wishlist.add(product=product) 

            return Response({
                "status": "success",
                "message": f"Successfully added {product.name} to Wishlist",
                # FIX #3: Calculate the cart quantity correctly
                "cart_quantity": len(wishlist), 
            }, status=status.HTTP_200_OK)
     
            
        except ProductModel.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {"error": "Invalid product ID or quantity"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while adding to cart"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CartSummaryAPIView(APIView):
    """API endpoint for the chatbot to view the user's cart."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # This view now works correctly with the fixed Cart class
        cart = Cart(request)
        cart_products = cart.get_cart_product() # Gets Product objects
        quantities = cart.get_quantity()        # Gets a dict of quantities {'id': qty}
        
        products_data = []
        # FIX: Loop through products and combine them with quantities
        for product in cart_products:
            product_id_str = str(product.product_id)
            quantity = quantities.get(product_id_str, 0)
            
            products_data.append({
                'product_id': product.product_id,
                'name': product.name,
                'quantity': quantity,
                'price': str(product.price),
                'total_price': str(float(product.price) * quantity)
            })

        response_data = {
            'status': 'success',
            'products': products_data,
            'cart_quantity': len(cart), # Use len(cart) for total items
            'total': str(cart.cart_total()),
            'gst_total': str(cart.cart_gsttotal())
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CartDeleteAPIView(APIView):
    """API endpoint for the chatbot to delete items from the user's cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            product_id = request.data.get('product_id')
            if not product_id:
                return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            product = get_object_or_404(ProductModel, product_id=int(product_id))
            
            cart = Cart(request)
            cart.delete(product=str(product_id))
            
            return Response({
                "status": "success",
                "message": f"Successfully removed {product.name} from your cart",
            }, status=status.HTTP_200_OK)
            
        except (ValueError, TypeError):
            return Response({"error": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CartUpdateAPIView(APIView):
    """API endpoint for the chatbot to update item quantities in the cart."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            product_id = request.data.get('product_id')
            quantity = request.data.get('product_qty')
            
            if not product_id or quantity is None:
                return Response({"error": "Product ID and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            product = get_object_or_404(ProductModel, product_id=int(product_id))
            
            cart = Cart(request)
            cart.update(product=str(product_id), quantity=int(quantity))
            
            return Response({
                "status": "success",
                "message": f"Successfully updated {product.name} quantity to {quantity}",
            }, status=status.HTTP_200_OK)
            
        except (ValueError, TypeError):
            return Response({"error": "Invalid product ID or quantity"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import JsonResponse
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Elasticsearch client
try:
    # Use the elasticsearch container name from your Docker setup
    es_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
    es_port = os.getenv("ELASTICSEARCH_PORT", "9200")
    es = Elasticsearch([f"http://{es_host}:{es_port}"])
except Exception as e:
    logger.error(f"Failed to connect to Elasticsearch: {e}")
    es = None

class ProductSearchAPIView(APIView):
    """API endpoint for chatbot to search products using Elasticsearch."""
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            query = request.GET.get("search", "").strip()
            print("Search query:", query)

            if not query:
                return Response({
                    "status": "error",
                    "message": "Search query is required",
                    "products": []
                }, status=status.HTTP_400_BAD_REQUEST)

            if not es:
                return Response({
                    "status": "error",
                    "message": "Search service is not available",
                    "products": []
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # Elasticsearch query for product search
            search_body = {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["name^3", "desc^2", "category.name"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            },
                            {
                                "match_phrase_prefix": {
                                    "name": {
                                        "query": query,
                                        "boost": 2
                                    }
                                }
                            },
                            {
                                "wildcard": {
                                    "name": {
                                        "value": f"*{query.lower()}*",
                                        "boost": 1.5
                                    }
                                }
                            }
                        ],
                        "minimum_should_match": 1
                    }
                },
                "sort": [
                    "_score",                 # relevance first
                    {"product_id": "asc"}     # fallback on product_id
                ],
                "size": 20,
                "_source": ["product_id", "name", "price", "unit", "stock", "desc", "category"]
            }

            response = es.search(index="products", body=search_body)

            # Process results
            products = []
            for hit in response['hits']['hits']:
                product = hit['_source']
                products.append({
                    "product_id": product.get('product_id'),
                    "name": product.get('name'),
                    "price": product.get('price'),
                    "unit": product.get('unit'),
                    "stock": product.get('stock'),
                    "desc": product.get('desc'),
                    "category": product.get('category', {}),
                    "score": hit['_score']
                })

            return Response({
                "status": "success",
                "message": f"Found {len(products)} products matching '{query}'",
                "products": products,
                "total_hits": response['hits']['total']['value']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in product search: {str(e)}")
            return Response({
                "status": "error",
                "message": "An error occurred while searching products",
                "products": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper function for other parts of the application
def search_products_elasticsearch(query, limit=20):
    if not es or not query:
        return []

    try:
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["name^3", "desc^2", "category.name"],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "name": {
                                    "query": query,
                                    "boost": 2
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "sort": [
                "_score",
                {"product_id": "asc"}
            ],
            "size": limit,
            "_source": ["product_id", "name", "price", "unit", "stock", "desc", "category"]
        }

        response = es.search(index="products", body=search_body)

        products = []
        for hit in response['hits']['hits']:
            product = hit['_source']
            products.append({
                "product_id": product.get('product_id'),
                "name": product.get('name'),
                "price": product.get('price'),
                "unit": product.get('unit'),
                "stock": product.get('stock'),
                "desc": product.get('desc'),
                "category": product.get('category', {}),
                "score": hit['_score']
            })

        return products

    except Exception as e:
        logger.error(f"Elasticsearch search error: {str(e)}")
        return []


# Enhanced version of your existing searchproduct view with fallback
def searchproduct(request):
    if request.method == "GET":
        query = request.GET.get("search")
        if query:
            try:
                products = search_products_elasticsearch(query, limit=50)
                if products:
                    product_ids = [p['product_id'] for p in products]
                    db_products = ProductModel.objects.filter(product_id__in=product_ids)

                    # Preserve Elasticsearch ordering
                    ordered_products = []
                    for es_product in products:
                        for db_product in db_products:
                            if db_product.product_id == es_product['product_id']:
                                ordered_products.append(db_product)
                                break

                    context = {"products": ordered_products}
                else:
                    context = {"products": []}
            except Exception as e:
                logger.warning(f"Elasticsearch failed, fallback to DB: {e}")
                results = ProductModel.objects.filter(
                    Q(name__icontains=query) | Q(category__category__icontains=query)
                )
                context = {"products": results}

            return JsonResponse({
                "html": render(request, "search_products.html", context).content.decode("utf-8")
            })
    return JsonResponse({"html": ""})

import threading
import time
import requests
import docker
from docker.errors import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# --- Configuration ---
# Find this by running `docker ps` after starting with the profile
OLLAMA_CONTAINER_NAME = "ps-thakkar_ollama" 
MODEL_TO_CHECK = "phi3:mini" # The model you want to use
RASA_SERVER_URL = "http://rasa:5005" # Hostname of the Rasa server inside Docker

# --- Helper Functions using Docker SDK ---

def get_ollama_container():
    """Finds and returns the ollama container object."""
    try:
        client = docker.from_env()
        return client.containers.get(OLLAMA_CONTAINER_NAME)
    except NotFound:
        print(f"Container '{OLLAMA_CONTAINER_NAME}' not found.")
        return None
    except Exception as e:
        print(f"Error connecting to Docker: {e}")
        return None

def is_ollama_running():
    """Checks if the ollama service is running using the SDK."""
    container = get_ollama_container()
    return container and container.status == 'running'

def start_ollama():
    """Starts the ollama container and waits for the specific model to be ready."""
    container = get_ollama_container()
    if not container:
        raise RuntimeError(f"Ollama container '{OLLAMA_CONTAINER_NAME}' was not found.")

    if container.status != 'running':
        print("Ollama is not running. Starting container...")
        container.start()
    
    print(f"Waiting for Ollama model '{MODEL_TO_CHECK}' to become available...")
    max_retries = 15  # Try for 75 seconds
    for i in range(max_retries):
        try:
            response = requests.get("http://ollama:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if MODEL_TO_CHECK in model.get("name"):
                        print(f"✅ Ollama model '{MODEL_TO_CHECK}' is loaded and ready.")
                        return
        except requests.exceptions.RequestException:
            pass
        
        print(f"Attempt {i+1}/{max_retries}: Ollama not ready yet, waiting 5 seconds...")
        time.sleep(5)
    
    raise RuntimeError(f"Ollama service or model '{MODEL_TO_CHECK}' did not become available in time.")

def stop_ollama():
    """Stops the ollama container using the Docker SDK."""
    container = get_ollama_container()
    if container and container.status == 'running':
        print("Ollama task complete. Stopping container.")
        container.stop()

# --- Background Worker & API View ---

def process_llm_request_task(conversation_id: str, question: str):
    """Runs in a background thread to handle the entire Ollama lifecycle."""
    print(f"Starting background task for conversation_id: {conversation_id}")
    rasa_callback_url = f"{RASA_SERVER_URL}/conversations/{conversation_id}/trigger_intent"
    
    try:
        start_ollama()
        
        ollama_url = "http://ollama:11434/api/generate"
        payload = {"model": MODEL_TO_CHECK, "prompt": question, "stream": False}
        
        response = requests.post(ollama_url, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        llm_answer = data.get("response", "Sorry, I couldn't process that.")

        requests.post(rasa_callback_url, json={
            "name": "EXTERNAL_llm_response_ready",
            "entities": {"llm_response": llm_answer}
        })
    except Exception as e:
        print(f"Error in background LLM task for {conversation_id}: {e}")
        requests.post(rasa_callback_url, json={
            "name": "EXTERNAL_llm_response_ready",
            "entities": {"llm_response": "Sorry, there was an error with the advanced knowledge base."}
        })
    finally:
        stop_ollama()

class ComplexSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Receives a request from Rasa and starts the background task."""
        question = request.data.get("question")
        conversation_id = request.data.get("conversation_id")

        if not question or not conversation_id:
            return Response({"error": "question and conversation_id are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        thread = threading.Thread(target=process_llm_request_task, args=(conversation_id, question))
        thread.start()

        return Response({"status": "processing_started"}, status=status.HTTP_202_ACCEPTED)