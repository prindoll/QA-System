from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.qa import router as qa_router
from app.core.config.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(qa_router, prefix="/qa", tags=["qa"])
