from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from app.core.config import get_settings
from app.core.database import init_db
from app.core.rate_limiter import limiter
from app.api.v1.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")
    yield
    # Shutdown
    print("Shutting down...")


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"

        return response


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A simple task management API built with FastAPI and SQLModel with rate limiting and security",
    lifespan=lifespan
)

# Set up rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware (must be before CORS)
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS - More restrictive for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    max_age=settings.CORS_MAX_AGE,
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint."""
    return {
        "message": "Welcome to Task Management API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
@limiter.limit("200/minute")
async def health_check(request: Request):
    """Health check endpoint."""
    return {"status": "healthy"}
