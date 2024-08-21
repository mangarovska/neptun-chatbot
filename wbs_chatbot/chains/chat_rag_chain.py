import os
import re
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

        print("\nInitial Recommended Products:")
        for idx, (name, specs, price) in enumerate(products, start=1):
            print(f"{idx}. Name: {name}\n   Specs: {specs}\n   Price: {price}")

        product_texts = "\n".join(
            [f"{i + 1}. Name: {name}\n   Specs: {specs}\n   Price: {price}" for i, (name, specs, price) in
             enumerate(products)])

        rerank_prompt = (
            f"Given the query: \"{query}\", please rerank the following products by their relevance:\n\n"
            f"{product_texts}\n\n"
            f"Start with the most relevant product. First, verify if the most relevant product meets the customer's specific request. "
            f"If the customer asks for a particular brand or specific requirements that are unavailable, respond with 'За жал немаме такви продукти' "
            f"(Unfortunately, we do not have such products). Kindly offer to recommend similar alternatives by saying, 'Можеме да ви понудиме слични продукти. "
            f"Дали би сакале да погледнете?' (We can suggest similar products. Would you like to see them?). "
            f"If suitable products are available, respond with 'Слични продукти кои ги препорачуваме' (We recommend these similar products). "
            f"In cases where only one product fully meets the criteria, say 'Ова одговара на вашите барања' (This meets your requirements) "
            f"and then suggest additional similar products with 'Слични продукти кои може да ви се допаѓаат' (Other similar products you may like). "
            f"If none of the products fulfill the request, conclude with 'Немаме такви продукти' (No such products available). "
            f"Please return the products in order of relevance, starting with the most relevant and only in Macedonian langauge."
        )

        #
        # rerank_prompt = (
        #     f"Given the query: \"{query}\", rerank the following products by relevance:\n\n"
        #     f"{product_texts}\n\n"
        #     f"Return products in the order of relevance, starting with the most relevant product.First check if most "
        #     f"relevant product is actually what the customer asked for,for example if they ask for a brand or "
        #     f"specifications that are not available, say that there are no such products or in macedonian За жал "
        #     f"немаме такви продукти. But if the most relevant ones are adequate say we can recommend these products - "
        #     f"Слични продукти кои ги препорачуваме. If there is only one relevant answer firslty say this is "
        #     f"adeqatue for your requirements - Ова одговара на вашите барања, and then reccomend othersimilar ones "
        #     f"that they may also like -Слични продукти кои може да ви се допаѓаат. If nothing fulfills the "
        #     f"requirements say that there are no such products, Немаме такви подукти."
        #     f"Please return  products in the order of relevance, starting with the most relevant product. If "
        #     # f"there is only one relevant product , return that one at first and say this is what "
        #     # f"you can find or in Macedonian Овој продукт одговара на вашите барања. But in another paragraph give "
        #     # f"other 2 or 3 recommendations that are next in the relevancy list, and say Исто така може да ви се допаѓа"
        #     # f"If there are not any products that fulfill the requirements but there are similar ones state that there "
        #     # f"are no exact products but here is something similar in Macedonian language.o
        #
        # )

        response = self.chat_model.invoke(rerank_prompt)
        reranked_products = response.content.strip().splitlines()
        clean_reranked_products = [re.sub(r'\*\*', '', product) for product in reranked_products]

        print("\nReranked Products:")
        for idx, product in enumerate(clean_reranked_products, start=1):
            print(f" {product}")

        return reranked_products


if __name__ == "__main__":
    recommender = ProductRecommender()
    # query = "сакам да го купам најевтиниот самсунг телевизор 55\""
    # recommended_products = recommender.recommend_products(query, "neptun-products")
