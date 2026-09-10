from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.database.models
from app.auth.routes import router as auth_router
from app.transactions.routes import router as transactions_router
from app.alerts.routes import router as alerts_router
from app.analysis.routes import router as analysis_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(alerts_router)
app.include_router(analysis_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}