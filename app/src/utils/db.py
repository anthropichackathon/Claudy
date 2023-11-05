import os

import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

from app.src.utils.openai import get_embedding, setup_openai

load_dotenv()
setup_openai()


def calculate_cosine_similarity(vector1, vector2):
    similarity = cosine_similarity([vector1], [vector2])
    return similarity[0][0]

class SingletonDataFrame:
    _instance = None
    _filename = "memory.csv"

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(SingletonDataFrame, cls).__new__(cls, *args, **kwargs)
            if os.path.exists(cls._filename):
                try:
                    print("Reading memory from file")
                    cls._instance.df = pd.read_csv(cls._filename)
                    cls._instance.df["embedding"] = cls._instance.df["embedding"].apply(lambda x: eval(x))
                    print(f"Memory file read, {len(cls._instance.df)} elements")
                except pd.errors.EmptyDataError:
                    print("Memory file is empty, creating a n ew one")
                    cls._instance.df = pd.DataFrame(columns=["content", "vec_id", "date", "embedding"])
            else:
                print("Creating new memory file")
                cls._instance.df = pd.DataFrame(columns=["content", "vec_id", "date", "embedding"])
        return cls._instance

    def get_df(self):
        return self.df

    def save_to_csv(self):
        self.df.to_csv(self._filename, index=False)

    def insert_embeddings(self, contents: list[dict], threshold=0.999):
        for item in contents:
            self._process_item(item, threshold)

    def _process_item(self, item: dict, threshold=0.999) -> dict:
        try:
            df = pd.DataFrame([item])
            df["vec_id"] = df["content"].apply(lambda x: "S" + str(abs(hash(x))))
            df["date"] = df["content"].apply(lambda x: str(pd.Timestamp.now()))
            df["embedding"] = df["content"].apply(
                lambda x: get_embedding(x, engine=os.getenv("EMBEDDING_DEPLOYMENT_NAME")))

            # Check if embedding already exists in the database
            insert_data = True
            for _, row in self.get_df().iterrows():
                similarity = calculate_cosine_similarity(row['embedding'], df['embedding'][0])
                if similarity >= threshold:
                    print("Not inserted, embedding already exists")
                    insert_data = False
                    break

            if insert_data:
                self.add_data(df)

            return {"message": f"Done"}
        except Exception as e:
            raise e

    def add_data(self, data):
        if isinstance(data, pd.DataFrame):
            new_df = pd.concat([self.df, data], ignore_index=True)
            self.df = new_df
            self.save_to_csv()
            print("Data added")
        else:
            raise ValueError("Data should be a DataFrame with columns: content, vec_id, date")

    def delete_data(self, vec_ids):
        if isinstance(vec_ids, (list, tuple)):
            self.df = self.df[~self.df['vec_id'].isin(vec_ids)]
            self.save_to_csv()
            print("Data deleted")
        elif isinstance(vec_ids, (int, str)):
            self.df = self.df[self.df['vec_id'] != vec_ids]
            self.save_to_csv()  #
            print("Data deleted")
        else:
            raise ValueError("vec_ids should be a list, tuple, integer, or string")
        print(len(self.df))

    def semantic_search(self, query: str, top_k=5) -> list[tuple[str, str, str, float]]:
        embedding_deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
        embedding = get_embedding(query, engine=embedding_deployment_name)

        similarities = []
        for _, row in self.get_df().iterrows():
            similarity = calculate_cosine_similarity(row['embedding'], embedding)
            similarities.append((row['content'], row['vec_id'], row['date'], similarity))

            # Sort by similarity and get the top k results
        similarities.sort(key=lambda x: x[3], reverse=True)
        top_results = similarities[:top_k]

        return top_results

    def get_latest_data(self, top_k=20) -> list[tuple[str, str, str, float]]:
        latest_obs = self.df.sort_values(by=['date'], ascending=False).head(1)
        latest_content = latest_obs['content'].values[0]

        most_similar = self.semantic_search(latest_content, top_k=top_k)
        return most_similar
