import logging
import sys

from fastapi import FastAPI

from src.routers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

app = FastAPI()
app.include_router(router, prefix="/api")
