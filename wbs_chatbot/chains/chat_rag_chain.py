import os
import re
import spacy
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from wbs_chatbot.chains.QueryHistory import QueryHistory  # Assuming this is your custom QueryHistory module
from langchain.globals import set_verbose

set_verbose(False)


class ProductRecommender:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self._load_api_keys()
        self._initialize_models()
        self.client = QdrantClient(url="http://localhost:6333")
        self.query_history = QueryHistory(chat_model=self.chat_model)

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

    def classify_intent(self, query: str) -> str:
        prompt = f"Classify the following query as either 'product_related' or 'conversational':\n\nQuery: \"{query}\""

        response = self.chat_model.invoke(prompt)
        intent = response.content.strip().lower()

        if 'product_related' in intent:
            return "product_related"
        else:
            return "conversational"

    def is_query_relevant(self, query: str, collection_name: str, relevance_threshold: float = 0.2) -> bool:
        intent = self.classify_intent(query)
        if intent != "product_related":
            return False

        # if the intent is product-related
        query_vector = self.embedding_model.embed_query(query)
        points = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=1  # check the most relevant product
        )

        # no results or relevance score is low
        if not points or points[0].score < relevance_threshold:
            return False

        return True

    def extract_constraints(self, query):
        brand = None
        size = None

        doc = self.nlp(query)
        for ent in doc.ents:
            if ent.label_ == "ORG":  # 'ORG' label in spaCy
                brand = ent.text.capitalize()
                break

        size_match = re.search(r"(\d{2,3}) инчи", query, re.IGNORECASE)
        if size_match:
            size = size_match.group(0)

        return {"brand": brand, "size": size}

    def recommend_products(self, query: str, collection_name: str, limit: int = 5):

        if not self.is_query_relevant(query, collection_name):
            return ["Не можам да го одговорам тоа прашање. Прашајте нешто друго за нашите продукти."]

        constraints = self.extract_constraints(query)

        previous_queries = self.query_history.get_previous_queries(query, analyze_with_ai=True)

        if isinstance(previous_queries, str):
            context_prompt = f"The customer previously asked:\n{previous_queries}\n\n"
        else:
            context_prompt = "\n".join(
                [f"Previous query: {q['query']}\nResponse: {q['response']}" for q in previous_queries])

        context_prompt += f"The customer is looking for products matching the following criteria:\n"
        if constraints["brand"]:
            context_prompt += f"- Brand: {constraints['brand']}\n"
        if constraints["size"]:
            context_prompt += f"- Size: {constraints['size']}\n"

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

        # Format the products for reranking by the language model
        product_texts = "\n".join(
            [f"{i + 1}. Name: {name}\n   Specs: {specs}\n   Price: {price}" for i, (name, specs, price) in
             enumerate(products)]
        )

        rerank_prompt = (
                context_prompt +
                f"Given the query: \"{query}\", please rerank the following products by their relevance to the customer's needs:\n\n"
                f"{product_texts}\n\n"
                f"Instructions:"
                f"1. Relevance check: First, verify if the most relevant product meets the customer's specific request. "
                f"For instance, if the customer is asking for a particular brand or specific feature that is not available, reply with 'За жал немаме такви продукти' "
                f"(Unfortunately, we do not have such products)."
                f"2. Specific Recommendations: If suitable products are available, respond with 'Слични продукти кои ги препорачуваме се следниве: ' (We recommend these similar products: ). "
                f"If only one product meets the criteria, say 'Ова одговара на вашите барања' (This meets your requirements) and suggest additional similar products with 'Слични продукти кои може да ви се допаѓаат' (Other similar products you may like). "
                f"If none of the products fulfill the request, conclude with 'Немаме такви продукти' (No such products available). "
                f"3. Output Format: Return the products in order of relevance, starting with the most relevant. Provide responses only in Macedonian. "
                f"Please ensure the final response is concise and adheres to these guidelines."
        )

        response = self.chat_model.invoke(rerank_prompt)
        reranked_products = response.content.strip().splitlines()

        self.query_history.save_query(query, reranked_products)

        clean_reranked_products = [re.sub(r'\*\*', '', product) for product in reranked_products]

        print("\nReranked Products:")
        for idx, product in enumerate(clean_reranked_products, start=1):
            print(f" {product}")

        return clean_reranked_products


if __name__ == "__main__":
    recommender = ProductRecommender()
    # query = "сакам да го купам најевтиниот самсунг телевизор 55\""
    # recommended_products = recommender.recommend_products(query, "neptun-products")
