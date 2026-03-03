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
from .core.migrate import run_migrations

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

# Mount static files for Railway (handles missing directories gracefully)
def mount_static_files():
    """Mount static files if frontend directory exists"""
    try:
        if not frontend_dir.exists():
            print("Note: Frontend directory not found, skipping static files")
            return
        
        # Mount CSS files
        css_dir = frontend_dir / "css"
        if css_dir.exists():
            app.mount("/static", StaticFiles(directory=str(css_dir), html=True), name="static")
        
        # Mount JS files
        js_dir = frontend_dir / "js"
        if js_dir.exists():
            app.mount("/js", StaticFiles(directory=str(js_dir), html=True), name="js")
        
        # Mount images
        images_dir = frontend_dir / "images"
        if images_dir.exists():
            app.mount("/images", StaticFiles(directory=str(images_dir), html=True), name="images")
            
        print(f"Frontend static files mounted from {frontend_dir}")
    except RuntimeError as e:
        print(f"Note: Static files not mounted - {e}")

mount_static_files()


@app.get("/")
async def serve_frontend():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "XANENE OPS API - Visit /docs for API documentation"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/api/run-migrations")
async def run_migrations_endpoint():
    """Manual migration endpoint - for debugging"""
    from .core.migrate import run_migrations
    success = run_migrations()
    return {"success": success, "message": "Migration completed" if success else "Migration failed"}


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
    # Run database migrations first
    run_migrations()
    create_initial_admin()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
