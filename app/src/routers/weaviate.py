import os
from dataclasses import dataclass,asdict
from typing import List

import pandas as pd
from fastapi import APIRouter
from fastapi import HTTPException
from weaviate import Client

from app.src.utils.openai import get_embedding
from app.src.utils.weaviate import query_db, get_all_elements, setup_main_class, insert_embeddings, add_class

__all__ = ["get_embeddings_router"]


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
    def __init__(self, client: Client):
        self.client = client
        self.class_name = os.getenv("VECTOR_CLASS_NAME")
        self.embedding_deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
        self.custom_content = {
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                },
                {
                    "name": "vec_id",
                    "dataType": ["text"],
                },
                {
                    "name": "date",
                    "dataType": ["text"],
                }
            ],
        }

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

    async def get_schemas(self) -> dict:
        try:
            return self.client.schema.get()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def setup_class() -> dict:
        try:
            setup_main_class()
            return {"message": "Class setup successful"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_class_count(self) -> dict:
        try:
            elements = get_all_elements().get("data").get("Get").get(self.class_name)
            return {"count": len(elements)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def insert_embedding(self, payload: InsertPayload) -> dict:
        try:
            df = pd.DataFrame([asdict(payload)])
            # hash by content
            df["vec_id"] = df["content"].apply(lambda x: str(abs(hash(x))))
            df["date"] = df["content"].apply(lambda x: str(pd.Timestamp.now()))
            df["embedding"] = df["content"].apply(lambda x: get_embedding(x, engine=self.embedding_deployment_name))
            insert_embeddings(
                db_client=self.client,
                class_name=self.class_name,
                content_df=df,
                check_existing_vec=True,
                batch_size=10,
                custom_content=self.custom_content
            )
            return {"message": "Insert successful"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def insert_embeddings(self, payload: InsertListPayload) -> dict:
        try:
            for item in payload.contents:
                df = pd.DataFrame([asdict(item)])
                df["vec_id"] = df["content"].apply(lambda x: str(abs(hash(x))))
                df["date"] = df["content"].apply(lambda x: str(pd.Timestamp.now()))
                df["embedding"] = df["content"].apply(lambda x: get_embedding(x, engine=self.embedding_deployment_name))
                insert_embeddings(
                    db_client=self.client,
                    class_name=self.class_name,
                    content_df=df,
                    check_existing_vec=True,
                    batch_size=10,
                    custom_content=self.custom_content
                )
            return {"message": "Insert successful"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_schema(self) -> dict:
        try:
            self.client.schema.delete_class(self.class_name)
            return {"message": "Class deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def init_schema(self) -> dict:
        try:
            add_class(
                self.client,
                self.class_name,
                self.custom_content
            )
            return {"message": "Class created"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_object(self, payload: DeletePayload) -> dict:
        try:
            return self.client.batch.delete_objects(
                class_name=self.class_name,
                where={
                    'path': ['vec_id'],
                    'operator': 'Like',
                    'valueText': payload.id
                },
            )
            return {"message": "Object deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_objects(self, payload: DeleteListPayload) -> dict:
        try:
            for item in payload.ids:
                self.client.batch.delete_objects(
                    class_name=self.class_name,
                    where={
                        'path': ['vec_id'],
                        'operator': 'Like',
                        'valueText': item.id
                    },
                )
            return {"message": "Objects deleted"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

def get_embeddings_router(client: Client):
    ltk = LongTermKnowledge(client)
    router = APIRouter()

    @router.post("/long_term_knowledge")
    async def get_info(payload: QueryPayload) -> dict:
        return await ltk.retrieve_info(payload)

    @router.get("/long_term_knowledge/schemas")
    async def get_schemas_route() -> dict:
        return await ltk.get_schemas()

    @router.get("/long_term_knowledge/setup")
    async def setup_class_route() -> dict:
        return await ltk.setup_class()

    @router.get("/long_term_knowledge/count")
    async def get_class_count_route() -> dict:
        return await ltk.get_class_count()

    @router.post("/long_term_knowledge/insert_one")
    async def get_class_count_route(payload: InsertPayload) -> dict:
        return await ltk.insert_embedding(payload)

    @router.post("/long_term_knowledge/insert_many")
    async def get_class_count_route(payload: InsertListPayload) -> dict:
        return await ltk.insert_embeddings(payload)

    @router.delete("/long_term_knowledge/delete")
    async def delete_schema_route() -> dict:
        return await ltk.delete_schema()

    @router.post("/long_term_knowledge/init")
    async def init_schema_route() -> dict:
        return await ltk.init_schema()

    @router.delete("/long_term_knowledge/delete_one")
    async def delete_object_route(payload: DeletePayload) -> dict:
        return await ltk.delete_object(payload)

    @router.delete("/long_term_knowledge/delete_many")
    async def delete_objects_route(payload: DeleteListPayload) -> dict:
        return await ltk.delete_objects(payload)

    return router
