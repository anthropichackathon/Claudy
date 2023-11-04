import os
from typing import Any, Dict, Optional, List

import numpy as np
import pandas as pd
import weaviate
from weaviate import Client
from weaviate import UnexpectedStatusCodeException

from app.src.logger.basic_logger import Logger

logger = Logger().get_logger()

__all__ = [
    "setup_main_class",
    "get_all_elements",
    "add_class",
    "check_if_vector_exists",
    "insert_embeddings",
    "query_db",
]


def setup_main_class():
    host = os.getenv("WEAVIATE_DB_HOST")
    client = Client(host)

    class_name = os.getenv("VECTOR_CLASS_NAME")

    custom_content = {
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
    add_class(client_db=client, class_name=class_name, custom_content=custom_content)


def get_all_elements():
    host = os.getenv("WEAVIATE_DB_HOST")
    client = Client(host)

    class_name = os.getenv("VECTOR_CLASS_NAME")
    vec = {"vector": np.random.rand(1536).tolist()}

    all_elements = (
        client
        .query.get(class_name, ["content", "vec_id", "date", "_additional {certainty}"])
        .with_near_vector(vec)
        .with_limit(1_000)
        .do()
    )

    return all_elements


def add_class(client_db: weaviate.Client, class_name: str,
              custom_content: Optional[Dict[str, Any]] = None) -> None:
    """
    Add class to vector DB

    Parameters
    ----------
    client_db: weaviate client for DB
    class_name: name of a class to be added
    custom_content: custom schema to be added, if None then there will be only "content"
    """
    try:
        _ = client_db.schema.get(class_name)
        logger.info(f"Class: {class_name} exist")
    except UnexpectedStatusCodeException:
        logger.info(f"Class: {class_name} does not exist, creating one")
        if custom_content:
            db_properties = custom_content
            assert len(db_properties.get("properties")) > 0, "Properties must be provided"
        else:
            db_properties = {
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"]
                    },
                ],
            }

        client_db.schema.create_class(
            {
                "class": class_name,
                "description": "Contains the paragraphs of text along with their embeddings",
                "vectorizer": "none",
                **db_properties,
            }
        )
        logger.info(f"Class: {class_name} added")


def insert_embeddings(db_client: weaviate.Client, class_name: str, content_df: pd.DataFrame, check_existing_vec: bool,
                      batch_size: int = 10, custom_content: Optional[Dict[str, Any]] = None) -> None:
    """
    Insert embeddings to DB.

    Parameters
    ----------
    db_client: weaviate client for DB
    class_name: name of a class in which elements which will be added
    content_df: dataframe with content and embeddings
    check_existing_vec: whether to check if vector already exists in DB
    batch_size: batch size for adding vectors, default 10
    custom_content: custom content to be added, if None then there will be only "content"
    """
    cnt = 0
    with db_client.batch as batch:
        batch.configure(batch_size=batch_size)
        n = content_df.shape[0]
        for index, row in content_df.iterrows():
            embedding = row["embedding"]
            if custom_content:
                custom_columns = [content["name"] for content in custom_content["properties"]]
                batch_data = {col: row[col] for col in custom_columns}
            else:
                batch_data = {"content": row["text"]}

            if check_existing_vec:
                vec_exists = check_if_vector_exists(db_client, class_name, embedding)
                if vec_exists:
                    continue
                else:
                    batch.add_data_object(data_object=batch_data, class_name=class_name, vector=embedding)
                    cnt += 1
            else:
                batch.add_data_object(data_object=batch_data, class_name=class_name, vector=embedding)
                cnt += 1
            logger.info(f"{index}/{n - 1}")
    logger.info(f"{cnt} embeddings added!")


def check_if_vector_exists(db_client: weaviate.Client, class_name: str, embedding: np.array,
                           threshold: float = 0.999) -> bool:
    """
    Checks if vector exists in DB

    Parameters
    ----------
    db_client: weaviate client for DB
    class_name: name of a class in which to make a check
    embedding: embedding of a text to be checked
    threshold: threshold for the certainty of the vector to be considered as existing, default 0.999

    Returns
    -------
    bool: True if vector exists, False otherwise
    """
    vec = {"vector": embedding}
    vec_in_db = (
        db_client
        .query
        .get(class_name, ["_additional {certainty}"])
        .with_near_vector(vec)
        .with_limit(1)
        .do()
    )
    vec_in_db_scores = (
        vec_in_db
        .get("data")
        .get("Get")
        .get(class_name)
    )
    if len(vec_in_db_scores) == 0:
        return False
    else:
        vec_in_db_score = (
            vec_in_db_scores
            .pop()
            .get("_additional")
            .get("certainty")
        )

    return vec_in_db_score > threshold


def query_db(db_client: weaviate.Client, class_name: str, vec: Dict[str, List[float]], top_k: int,
             columns: List[str]) -> List[Dict[str, str]]:
    db_result = (
        db_client
        .query.get(class_name, columns)
        .with_near_vector(vec)
        .with_limit(top_k)
        .do()
        .get("data")
        .get("Get")
        .get(class_name)
    )

    return db_result
