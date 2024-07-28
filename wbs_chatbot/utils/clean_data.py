import pandas as pd
from pandas import DataFrame


def load_data() -> DataFrame | None:
    try:
        df = pd.read_csv(r"C:\Users\ana_m\OneDrive\Desktop\wbs-chatbot\wbs_chatbot\data\products-Neptun.csv")
        df.drop_duplicates(inplace=True)

        df.dropna(subset=['Name', 'Price'], inplace=True)

        df['Price'] = df['Price'].astype(str)
        df['Happy Price'] = df['Happy Price'].astype(str)

        print("Before conversion:")
        print(df[['Price', 'Happy Price']].head(40))

        df['Price'] = df['Price'].str.replace('.0', '', regex=False)
        df['Happy Price'] = df['Happy Price'].str.replace('.0', '', regex=False)

        df['Price'] = df['Price'].str.replace('.', '', regex=False)
        df['Happy Price'] = df['Happy Price'].str.replace('.', '', regex=False)

        print("After conversion:")
        print(df[['Price', 'Happy Price']].head(40))

        df.to_csv(r"C:\Users\ana_m\OneDrive\Desktop\wbs-chatbot\wbs_chatbot\data\cleaned_data.csv", index=False)
        return df

    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return None


load_data()
