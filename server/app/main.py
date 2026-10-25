from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.routes import router

app = FastAPI(title="SprintForge API", description="Project and task management API for a software engineering portfolio.", version="1.0.0")
origins = [origin.strip() for origin in settings.client_origin.split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
app.include_router(router)

@app.on_event("startup")
def create_tables_for_local_development() -> None:
    # create_all simplifies local setup; use Alembic migrations before production schema changes.
    Base.metadata.create_all(bind=engine)
