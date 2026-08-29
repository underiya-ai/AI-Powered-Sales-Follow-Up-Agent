from fastapi import FastAPI

from backend.api.conversation import router as conversations_router


app = FastAPI(
    title="FollowAI",
    description="AI-powered Sales Follow-Up Agent",
    version="1.0.0"
)


app.include_router(conversations_router)


@app.get("/")
async def root():
    return {
        "message": "FollowAI API is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }