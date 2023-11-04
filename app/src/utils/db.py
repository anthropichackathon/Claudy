import os

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


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
            self.save_to_csv() #
            print("Data deleted")
        else:
            raise ValueError("vec_ids should be a list, tuple, integer, or string")
        print(len(self.df))
