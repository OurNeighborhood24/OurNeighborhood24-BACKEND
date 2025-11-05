from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.database import init_db
from api.users.router import router as users_router
from api.auth.router import router as auth_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


@app.on_event("startup")
async def startup_event():
    print(f"=� {settings.app_name} is starting...")


@app.on_event("shutdown")
async def shutdown_event():
    print(f"=K {settings.app_name} is shutting down...")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Joint Hackathon API",
        "status": "ok",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# 라우터 등록
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )