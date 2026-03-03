from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .core.database import Base, engine
from .core.config import settings
from .api import auth_router, events_router, tasks_router, dashboard_router
from .models import User, UserRole
from .core.security import get_password_hash

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Operational system for Xa Nene - Circular Economy Company",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

# Serve static files (if frontend exists)
frontend_dir = Path(__file__).parent.parent.parent / "frontend"

# Only mount static files if directories exist (handles Railway deployment)
try:
    if (frontend_dir / "css").exists() and (frontend_dir / "js").exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dir / "css"), html=True), name="static")
        app.mount("/js", StaticFiles(directory=str(frontend_dir / "js"), html=True), name="js")
except RuntimeError as e:
    print(f"Note: Static files not mounted - {e}")


@app.get("/")
async def serve_frontend():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "XANENE OPS API - Visit /docs for API documentation"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


def create_initial_admin():
    """Create initial admin user if none exists"""
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    try:
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            admin = User(
                email="admin@xanene.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.commit()
            print("Initial admin user created: admin@xanene.com / admin123")
    except Exception as e:
        print(f"Warning: Could not create initial admin: {e}")
    finally:
        db.close()


# Create initial admin on startup
@app.on_event("startup")
async def startup_event():
    create_initial_admin()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
