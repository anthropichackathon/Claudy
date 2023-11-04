from dotenv import load_dotenv
from fastapi import FastAPI

from app.src.logger.basic_logger import Logger
from app.src.routers.db import get_embeddings_router
from app.src.routers.main import get_basic_router
from app.src.utils.openai import setup_openai
from src.utils.db import SingletonDataFrame

load_dotenv()

logger = Logger().get_logger()
setup_openai()

db_instance = SingletonDataFrame()
db = db_instance.get_df()

app = FastAPI(title="Embedding query API")
app.include_router(get_basic_router())
app.include_router(get_embeddings_router(db_instance))


logger.info(f"Df count: {db.shape}")
logger.info(f"App works: {app}")
