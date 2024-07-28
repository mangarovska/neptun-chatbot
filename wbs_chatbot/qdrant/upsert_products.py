from typing import List

import pandas as pd
from wbs_chatbot.qdrant.qdrant import Product, upsert_record
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
from wbs_chatbot.templates.upser_product_template import upsert_product_template


def csv_to_df(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def df_to_products(df: pd.DataFrame) -> list:
    print(df.head(10))
    products = []
    for _, row in df.iterrows():
        product = Product(
            category=row['Category'],
            name=row['Name'],
            price=int(row['Price']),
            happy_price=int(row['Happy Price']) if pd.notna(row['Happy Price']) else None,
            specs=row['Specifications'] if pd.notna(row['Specifications']) else ''
        )
        products.append(product)
    return products


def upsert_products(
        file_path: str = r"C:\Users\ana_m\OneDrive\Desktop\wbs-neptun-chatbot\wbs_chatbot\data\cleaned_data.csv"
) -> None:
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set it in the .env file.")

    df = csv_to_df(file_path)
    products: List[Product] = df_to_products(df)

    embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")

    for product in tqdm(products, desc="Upserting products:"):
        vector = embedding_model.embed_query(upsert_product_template(product))
        upsert_record(product=product, vector=vector)


upsert_products()

