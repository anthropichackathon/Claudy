import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from weaviate import Client

from app.src.routers.main import get_basic_router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Client(os.getenv("WEAVIATE_DB_HOST"))

app = FastAPI(title="Embedding query API")
app.include_router(get_basic_router())

logger.info(f"Weaviate Client: {client}")
logger.info(f"App works: {app}")
