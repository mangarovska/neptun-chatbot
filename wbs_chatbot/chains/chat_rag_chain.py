import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain.globals import set_verbose

set_verbose(True)


class ProductRecommender:
    def __init__(self):
        self._load_api_keys()
        self._initialize_models()
        self.client = QdrantClient(url="http://localhost:6333")

    def _load_api_keys(self):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

    def _initialize_models(self):
        self.chat_model = ChatOpenAI(model="gpt-4o", openai_api_key=self.openai_api_key)
        self.embedding_model = OpenAIEmbeddings(api_key=self.openai_api_key, model="text-embedding-3-small")

    def recommend_products(self, query: str, collection_name: str, limit: int = 5):
        query_vector = self.embedding_model.embed_query(query)
        points = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        return [point.payload["name"] for point in points]


if __name__ == "__main__":
    recommender = ProductRecommender()
    # query = "Сакам 27 инчен монитор за гејмање и да е Самсунг."
    # recommended_products = recommender.recommend_products(query, "neptun-products")
    # for product in recommended_products:
    #     print(product)
