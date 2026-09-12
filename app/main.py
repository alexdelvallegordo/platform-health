from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(
    title="Platform Health",
    description="Platform health and reliability monitoring service.",
    version="0.1.0",
)

app.include_router(health_router)
