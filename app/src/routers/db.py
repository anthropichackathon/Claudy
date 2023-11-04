import os
from dataclasses import dataclass, asdict
from typing import List

import pandas as pd
from fastapi import APIRouter
from fastapi import HTTPException

from app.src.utils.openai import get_embedding

__all__ = ["get_embeddings_router"]

from src.utils.db import calculate_cosine_similarity, SingletonDataFrame


@dataclass
class QueryPayload:
    query: str
    top_k: int


@dataclass
class InsertPayload:
    content: str


@dataclass
class InsertListPayload:
    contents: List[InsertPayload]


@dataclass
class DeletePayload:
    id: str


@dataclass
class DeleteListPayload:
    ids: List[DeletePayload]


class LongTermKnowledge:
    def __init__(self, db: SingletonDataFrame):
        self.db = db
        self.embedding_deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")

    async def retrieve_info(self, payload: QueryPayload) -> dict:
        query = payload.query
        top_k = payload.top_k

        embedding = get_embedding(query, engine=self.embedding_deployment_name)
        vec = {"vector": embedding}

        db_result = query_db(
            db_client=self.client,
            class_name=self.class_name,
            vec=vec,
            top_k=top_k,
            columns=["content", "vec_id", "date"]
        )
        return {"result": db_result}

    async def get_class_count(self) -> dict:
        try:
            elements = self.db.get_df()
            return {"count": len(elements)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def insert_embedding(self, payload: InsertPayload, threshold=0.999) -> dict:
        try:
            df = pd.DataFrame([asdict(payload)])
            df["vec_id"] = df["content"].apply(lambda x: "S"+str(abs(hash(x))))
            df["date"] = df["content"].apply(lambda x: str(pd.Timestamp.now()))
            df["embedding"] = df["content"].apply(lambda x: get_embedding(x, engine=self.embedding_deployment_name))

            # Check if embedding already exists in the database
            for _, row in self.db.get_df().iterrows():
                similarity = calculate_cosine_similarity(row['embedding'], df['embedding'][0])
                if similarity >= threshold:
                    return {"message": "Not inserted, embedding already exists"}

            self.db.add_data(df)
            return {"message": "Insert successful"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def insert_embeddings(self, payload: InsertListPayload, threshold=0.999) -> dict:
        try:
            for item in payload.contents:
                df = pd.DataFrame([asdict(item)])
                df["vec_id"] = df["content"].apply(lambda x: "S"+str(abs(hash(x))))
                df["date"] = df["content"].apply(lambda x: str(pd.Timestamp.now()))
                df["embedding"] = df["content"].apply(lambda x: get_embedding(x, engine=self.embedding_deployment_name))

                # Check if embedding already exists in the database
                insert_data = True
                for _, row in self.db.get_df().iterrows():
                    similarity = calculate_cosine_similarity(row['embedding'], df['embedding'][0])
                    if similarity >= threshold:
                        print("Not inserted, embedding already exists")
                        insert_data = False
                        break

                if insert_data:
                    self.db.add_data(df)

            return {"message": f"Done"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def reset_schema(self) -> dict:
        try:
            self.db = pd.DataFrame(columns=["content", "vec_id", "date"])
            return {"message": "Class deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_object(self, payload: DeletePayload) -> dict:
        try:
            print(payload.id)
            self.db.delete_data(payload.id)
            return {"message": "Object deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_objects(self, payload: DeleteListPayload) -> dict:
        try:
            for item in payload.ids:
                self.db.delete_data(item.id)
            return {"message": "Objects deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


def get_embeddings_router(db: SingletonDataFrame):
    ltk = LongTermKnowledge(db)
    router = APIRouter()

    @router.post("/long_term_knowledge")
    async def get_info(payload: QueryPayload) -> dict:
        return await ltk.retrieve_info(payload)

    @router.get("/long_term_knowledge/count")
    async def get_class_count_route() -> dict:
        return await ltk.get_class_count()

    @router.post("/long_term_knowledge/insert_one")
    async def get_class_count_route(payload: InsertPayload) -> dict:
        return await ltk.insert_embedding(payload)

    @router.post("/long_term_knowledge/insert_many")
    async def get_class_count_route(payload: InsertListPayload) -> dict:
        return await ltk.insert_embeddings(payload)

    @router.delete("/long_term_knowledge/reset")
    async def delete_schema_route() -> dict:
        return await ltk.reset_schema()

    @router.delete("/long_term_knowledge/delete_one")
    async def delete_object_route(payload: DeletePayload) -> dict:
        return await ltk.delete_object(payload)

    @router.delete("/long_term_knowledge/delete_many")
    async def delete_objects_route(payload: DeleteListPayload) -> dict:
        return await ltk.delete_objects(payload)

    return router
