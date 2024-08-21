import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain.globals import set_verbose

set_verbose(False)


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
        self.chat_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature="0",
            openai_api_key=self.openai_api_key
        )
        self.embedding_model = OpenAIEmbeddings(
            api_key=self.openai_api_key,
            model="text-embedding-3-small"
        )

    def is_query_relevant(self, query: str, collection_name: str, relevance_threshold: float = 0.3) -> bool:
        query_vector = self.embedding_model.embed_query(query)

        # perform a quick search with a high limit to check relevance
        points = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=1  # one point to check the most relevant product
        )

        # If there are no results or the relevance score is too low, mark as irrelevant
        if not points or points[0].score < relevance_threshold:
            return False

        return True

    def recommend_products(self, query: str, collection_name: str, limit: int = 5):

        # check if the query is relevant before proceeding
        if not self.is_query_relevant(query, collection_name):
            return [
                "Не можам да го одговорам тоа прашање. Прашајте нешто друго за нашите продукти."]

        query_vector = self.embedding_model.embed_query(query)
        points = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )

        products = [
            (point.payload["name"], point.payload["specs"], point.payload["price"])
            for point in points
        ]

        print("\nInitial Recommended Products:")
        for idx, (name, specs, price) in enumerate(products, start=1):
            print(f"{idx}. Name: {name}\n   Specs: {specs}\n   Price: {price}")

        product_texts = "\n".join(
            [f"{i + 1}. Name: {name}\n   Specs: {specs}\n   Price: {price}" for i, (name, specs, price) in
             enumerate(products)])

        rerank_prompt = (
            f"Given the query: \"{query}\", rerank the following products by relevance:\n\n"
            f"{product_texts}\n\n"
            f"Please return the list in the order of relevance, starting with the most relevant product."
        )

        response = self.chat_model.invoke(rerank_prompt)
        reranked_products = response.content.strip().splitlines()
        clean_reranked_products = [re.sub(r'\*\*', '', product) for product in reranked_products]

        print("\nReranked Products:")
        for idx, product in enumerate(clean_reranked_products, start=1):
            print(f" {product}")

        return clean_reranked_products


if __name__ == "__main__":
    recommender = ProductRecommender()
    # query = "сакам да го купам најевтиниот самсунг телевизор 55\""
    # recommended_products = recommender.recommend_products(query, "neptun-products")
