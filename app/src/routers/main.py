from typing import Dict

from fastapi import APIRouter

__all__ = ["get_basic_router"]


async def read_root() -> Dict[str, str]:
    return {"App": "Claudie - your new AI LLM assistant"}


async def health_check() -> Dict[str, str]:
    return {"Check": "App works"}


def get_basic_router():
    router = APIRouter()

    @router.get("/")
    async def get_root() -> Dict[str, str]:
        return await read_root()

    @router.get("/health")
    async def get_health() -> Dict[str, str]:
        return await health_check()

    return router
