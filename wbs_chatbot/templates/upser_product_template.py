from wbs_chatbot.qdrant.qdrant import Product


def upsert_product_template(
    product: Product
):
    return (f"Категорија на продукт:{product.category}\n\n"
            f"Име на продукт:{product.name}\n\n"
            f"Спецификации на продукт:{product.specs}")
