import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
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
        self.chat_model = ChatOpenAI(model="gpt-4", openai_api_key=self.openai_api_key)
        self.embedding_model = OpenAIEmbeddings(api_key=self.openai_api_key, model="text-embedding-3-small")

    def recommend_products(self, query: str, collection_name: str, limit: int = 5):
        # Step 1: Get the top-K results based on embeddings
        query_vector = self.embedding_model.embed_query(query)
        points = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        products = [point.payload["name"] for point in points]
        print("\nInitial Recommended Products:")
        for idx, product in enumerate(products, start=1):
            print(f"{idx}. {product}")


        product_texts = "\n".join([f"{i+1}. {product}" for i, product in enumerate(products)])
        rerank_prompt = f"Given the query: \"{query}\", rerank the following products by relevance:\n\n{product_texts}\n\nPlease return the list in the order of relevance, starting with the most relevant product."


        response = self.chat_model.invoke(rerank_prompt)


        reranked_products = response.content.splitlines()


        print("\nReranked Products:")
        for idx, product in enumerate(reranked_products, start=1):
            print(f"{idx}. {product}")
        return reranked_products

if __name__ == "__main__":
    recommender = ProductRecommender()
    query = "Сакам електрично ѓезве."
    recommended_products = recommender.recommend_products(query, "neptun-products")