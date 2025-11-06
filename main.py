from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.database import init_db
from api.users.router import router as users_router
from api.auth.router import router as auth_router
from api.reports.router import router as reports_router
from api.notifications.router import router as notifications_router
from api.routes.router import router as routes_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # 명시적으로 False
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(reports_router, prefix="/reports", tags=["reports"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(routes_router, prefix="/routes", tags=["routes"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )