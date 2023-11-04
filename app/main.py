import os

from dotenv import load_dotenv
from fastapi import FastAPI
from weaviate import Client

from app.src.routers.main import get_basic_router
from app.src.logger.basic_logger import Logger
from app.src.routers.weaviate import get_embeddings_router
from app.src.utils.openai import setup_openai

load_dotenv()

logger = Logger().get_logger()
setup_openai()

client = Client(os.getenv("WEAVIATE_DB_HOST"))

app = FastAPI(title="Embedding query API")
app.include_router(get_basic_router())
app.include_router(get_embeddings_router(client))

logger.info(f"Weaviate Client: {client}")
logger.info(f"App works: {app}")
