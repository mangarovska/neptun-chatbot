from typing import List, Optional
import uuid
from pydantic import BaseModel
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")


class Product(BaseModel):
    name: Optional[str]
    category: str
    price: int
    happy_price: Optional[int] | None
    specs: Optional[str]


def upsert_record(vector: List[float], product: Product):
    unique_id = str(uuid.uuid4())

    client.upsert(
        collection_name="neptun-products",
        points=[
            models.PointStruct(
                id=unique_id,
                payload={
                    "category": product.category,
                    "price": product.price,
                    "happy_price": product.happy_price,
                    "specs": product.specs,
                },
                vector=vector,
            ),
        ],
    )
