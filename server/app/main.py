from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.routes import router

@asynccontextmanager
async def lifespan(_: FastAPI):
    # The first deploy needs its tables; use Alembic before future schema changes.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SprintForge API",
    description="Project and task management API for a software engineering portfolio.",
    version="1.0.0",
    lifespan=lifespan,
)
origins = [origin.strip() for origin in settings.client_origin.split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
app.include_router(router)
