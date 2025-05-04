class ProductMapping:
    index_name = "products"
    mappings = {
        "mappings": {
            "properties": {
                "product_id": {"type": "integer"},
                "name": {"type": "text"},
                "price": {"type": "float"},
                "unit": {"type": "keyword"},
                "stock": {"type": "float"},
                "desc": {"type": "text"},
                "category": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "text"},
                    },
                },
            }
        }
    }


class UserMapping:
    index_name = "users"
    mappings = {
        "mappings": {
            "properties": {
                "user_id": {"type": "integer"},
                "username": {"type": "keyword"},
                "email": {"type": "keyword"},
                "phone": {"type": "keyword"},
                "Address": {"type": "text"},
                "shipping_address_model": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "shipping_first_name": {"type": "text"},
                        "shipping_last_name": {"type": "text"},
                        "shipping_address": {"type": "text"},
                        "shipping_city": {"type": "text"},
                        "shipping_state": {"type": "text"},
                    },
                },
            }
        }
    }