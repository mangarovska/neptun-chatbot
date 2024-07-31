import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain.globals import set_verbose

# Disable verbose mode for cleaner output
set_verbose(False)


class ProductRecommender:
    def __init__(self):
        self._load_api_keys()
        self._initialize_models()
        self.client = QdrantClient(url="http://localhost:6333")

    def _load_api_keys(self):
        """
        Load API keys from the .env file and set them as class attributes.
        """
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set it in the .env file.")

    def _initialize_models(self):
        """
        Initialize the models required for embeddings and chat.
        """
        self.chat_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature="0",
            openai_api_key=self.openai_api_key
        )
        self.embedding_model = OpenAIEmbeddings(
            api_key=self.openai_api_key,
            model="text-embedding-3-small"
        )

    def recommend_products(self, query: str, collection_name: str, limit: int = 10):

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

        # Print initial recommended products
        print("\nInitial Recommended Products:")
        for idx, (name, specs, price) in enumerate(products, start=1):
            print(f"{idx}. Name: {name}\n   Specs: {specs}    \nPrice: {price}")

        product_texts = "\n".join(
            [f"{i + 1}. Name: {name}\n   Specs: {specs}    \nPrice: {price}" for i, (name, specs, price) in enumerate(products)])
        rerank_prompt = (
            f"Given the query: \"{query}\", rerank the following products by relevance:\n\n"
            f"{product_texts}\n\n"
            f"Please return the list in the order of relevance, starting with the most relevant product."
        )

        response = self.chat_model.invoke(rerank_prompt)
        reranked_products = response.content.splitlines()

        print("\nReranked Products:")
        for idx, product in enumerate(reranked_products, start=1):
            print(f" {product}")

        return reranked_products


if __name__ == "__main__":
    recommender = ProductRecommender()
    # query = "сакам да го купам најевтиниот самсунг телевизор 55\""
    # recommended_products = recommender.recommend_products(query, "neptun-products")
