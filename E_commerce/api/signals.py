from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from elasticsearch import Elasticsearch
from api.models import ProductModel
from api.documents import ProductMapping
import logging
import os   

es_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
es_port = os.getenv("ELASTICSEARCH_PORT", "9200")
es = Elasticsearch([f"http://{es_host}:{es_port}"])
logger = logging.getLogger(__name__)
try:
    if not es.indices.exists(index=ProductMapping.index_name):
        logger.info(f"Creating index: {ProductMapping.index_name}")
        es.indices.create(index=ProductMapping.index_name, body=ProductMapping.mappings)
    else:
        logger.info(f"Index {ProductMapping.index_name} already exists.")
except ConnectionError as e:
    logger.error(f"Elasticsearch connection error: {e}")


@receiver(post_save, sender=ProductModel)
def update_product_index(sender, instance, **kwargs):
    logger.info("signal call Updating product index...")
    doc = {
        "product_id": instance.product_id,
        "name": instance.name,
        "price": instance.price,
        "unit": instance.unit,
        "stock": instance.stock,
        "desc": instance.desc,
        "category": {
            "id": instance.category.category_id,
            "name": instance.category.category,
        },
    }
    logger.info(doc)
    es.index(index=ProductMapping.index_name, id=instance.product_id, body=doc)

@receiver(post_delete, sender=ProductModel)
def delete_product_index(sender, instance, **kwargs):
    logger.info("signal call Deleting product index...")
    es.delete(index=ProductMapping.index_name, id=instance.product_id)