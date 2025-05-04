import time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError, ConnectionError
from django.conf import settings
from .documents import ProductMapping  # Adjust the import if needed

max_retries = 10
retry_delay = 5

for attempt in range(max_retries):
    try:
        es = Elasticsearch(settings.ELASTICSEARCH_DSL['default']['hosts'])

        if not es.indices.exists(index=ProductMapping.index_name):
            es.indices.create(index=ProductMapping.index_name, body=ProductMapping.mappings)
            print(f"✅ Created index: {ProductMapping.index_name}")
        else:
            print(f"ℹ️ Index already exists: {ProductMapping.index_name}")
        break  # success! Exit the retry loop

    except ConnectionError:
        print(f"❌ Elasticsearch not ready yet... retrying in {retry_delay} seconds (Attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)

    except RequestError as e:
        print(f"❌ Failed to create index {ProductMapping.index_name} due to invalid request: {e.info}")
        break

    except Exception as e:
        print(f"❌ Unexpected error while creating index {ProductMapping.index_name}: {str(e)}")
        break
else:
    print(f"❌ Failed to connect to Elasticsearch after {max_retries} attempts.")
