import os
import sys
import logging
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from api.documents import ProductMapping, UserMapping
from api.models import ProductModel
from customer.models import CustomUser

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    force=True
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Index data into Elasticsearch"

    def handle(self, *args, **kwargs):
        es_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
        es_port = os.getenv("ELASTICSEARCH_PORT", "9200")
        es = Elasticsearch([f"http://{es_host}:{es_port}"])

        if not es.indices.exists(index=ProductMapping.index_name):
            logger.info(f"Creating index: {ProductMapping.index_name}")
            es.indices.create(index=ProductMapping.index_name, body=ProductMapping.mappings)
        else:
            logger.info(f"Index {ProductMapping.index_name} already exists")

        logger.info("Indexing products...")
        products = ProductModel.objects.all()
        for product in products:
            doc = {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "unit": product.unit,
                "stock": product.stock,
                "desc": product.desc,
                "category": {
                    "id": product.category.category_id if product.category else None,
                    "name": product.category.category if product.category else None,
                },
            }
            es.index(index=ProductMapping.index_name, id=product.product_id, body=doc)

        if not es.indices.exists(index=UserMapping.index_name):
            logger.info(f"Creating index: {UserMapping.index_name}")
            es.indices.create(index=UserMapping.index_name, body=UserMapping.mappings)
        else:
            logger.info(f"Index {UserMapping.index_name} already exists")

        logger.info("Indexing users...")
        users = CustomUser.objects.all()
        for user in users:
            doc = {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "Address": user.Address,
                "shipping_address_model": {
                    "id": user.shipping_address_model.id if user.shipping_address_model else None,
                    "shipping_first_name": user.shipping_address_model.shipping_first_name if user.shipping_address_model else None,
                    "shipping_last_name": user.shipping_address_model.shipping_last_name if user.shipping_address_model else None,
                    "shipping_address": user.shipping_address_model.shipping_address if user.shipping_address_model else None,
                    "shipping_city": user.shipping_address_model.shipping_city if user.shipping_address_model else None,
                    "shipping_state": user.shipping_address_model.shipping_state if user.shipping_address_model else None,
                },
            }
            es.index(index=UserMapping.index_name, id=user.id, body=doc)

        logger.info("Data indexed successfully!")