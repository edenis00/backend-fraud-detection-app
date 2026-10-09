import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

import app.database.models
from app.auth.routes import router as auth_router
from app.transactions.routes import router as transactions_router
from app.alerts.routes import router as alerts_router
from app.analysis.routes import router as analysis_router
from app.reports.routes import router as reports_router
from app.departments.routes import router as departments_router
from app.cards.routes import router as cards_router
from app.fraud_rules.routes import router as fraud_rules_router
from app.audit.routes import router as audit_router
from app.breakdown.route import router as breakdown_router
from app.admin.routes import router as admin_router
from app.core.config import get_settings
from app.database.base import Base
from app.database.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(alerts_router)
app.include_router(analysis_router)
app.include_router(reports_router)
app.include_router(departments_router)
app.include_router(cards_router)
app.include_router(fraud_rules_router)
app.include_router(audit_router)
app.include_router(breakdown_router)
app.include_router(admin_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
