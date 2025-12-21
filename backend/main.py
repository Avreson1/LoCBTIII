from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.routers import auth, admin, student, license
from fastapi import Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database import SessionLocal
from backend.license_utils import check_license
import os

app = FastAPI(title="LoCBTIII API")

# License Middleware (Applied to API routes)
@app.middleware("http")
async def license_check_middleware(request: Request, call_next):
    # Allow some paths without license (e.g., license activation, static files if served here, payment)
    path = request.url.path
    if path.startswith("/api") and not any(p in path for p in ["/license", "/payment"]):
        # Check license
        db = SessionLocal()
        try:
            if not check_license(db):
                # Return 403 Forbidden with custom header/body
                # Middleware response construction is a bit manual in FastAPI
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "License Required", "code": "LICENSE_REQUIRED"}
                )
        finally:
            db.close()

    response = await call_next(request)
    return response

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(student.router, prefix="/api")
app.include_router(license.router, prefix="/api")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5173", # Vite default
    "http://127.0.0.1:5173",
    "*" # For local network access
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow API requests to pass through
        if full_path.startswith("api"):
            return {"error": "Not Found"}

        # Serve index.html for React Router
        if "." not in full_path:
             return FileResponse(os.path.join(frontend_path, "index.html"))

        # Serve static files if they exist
        file_path = os.path.join(frontend_path, full_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)

        # Fallback to index.html
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "CBT API is running (Frontend not found)"}
