"""
FastAPI application entry point for the Textures project.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Textures API",
    description="Human-in-the-loop texture generation system",
    version="0.1.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated images
images_dir = os.getenv("IMAGES_DIR", "./data/images")
# Convert to absolute path if relative
if not os.path.isabs(images_dir):
    # Go up from backend/src to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    images_dir = os.path.join(project_root, images_dir.lstrip("./"))
print(f"Static images directory: {images_dir}")
if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")
    print(f"✓ Images mounted at /images")
else:
    print(f"⚠ Images directory does not exist: {images_dir}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Textures API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "api_version": "0.1.0",
        "environment": os.getenv("ENV", "development")
    }

# Import and include API routers
try:
    from api import themes, images, generate, analytics
except ImportError:
    # Fallback for when running as module
    from .api import themes, images, generate, analytics

app.include_router(themes.router, prefix="/api/themes", tags=["themes"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(generate.router, prefix="/api/generate", tags=["generation"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
