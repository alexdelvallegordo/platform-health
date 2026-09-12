from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.status import router as status_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "Platform health, reliability and "
        "observability service."
    ),
    version=settings.app_version,
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.include_router(dashboard_router)
app.include_router(health_router)
app.include_router(status_router)
app.include_router(metrics_router)
