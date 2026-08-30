from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.conversation import router as conversations_router


app = FastAPI(
    title="FollowAI",
    description="AI-powered Sales Follow-Up Agent",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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