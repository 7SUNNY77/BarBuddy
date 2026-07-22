from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_cocktails import router as cocktails_router
from app.api.routes_meta import router as meta_router

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.limiter import limiter

app = FastAPI(
    title="BarBuddy API",
    description="API для каталога и рекомендаций коктейлей BarBuddy",
    version="0.2.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://bar-buddy-hzs5.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cocktails_router)
app.include_router(meta_router)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "BarBuddy API",
        "version": "0.2.0",
    }