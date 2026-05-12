from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.database.connection import engine

from app.core.firebase import init_firebase


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    yield
    await engine.dispose()


app = FastAPI(title="Luggage Pro", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
