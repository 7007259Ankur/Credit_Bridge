from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api import auth, consent, scoring, admin, psychometric

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="CreditBridge API",
    version="1.0.0",
    description="Explainable multi-agent credit scoring platform",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(consent.router, prefix="/api")
app.include_router(scoring.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(psychometric.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "creditbridge-api"}
