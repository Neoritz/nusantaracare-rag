from fastapi import FastAPI

from app.schemas import ChatRequest, ChatResponse
from app.services.agent import answer_question


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="NusantaraCare RAG API",
    version="1.0.0"
)


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def root():

    return {
        "message": "NusantaraCare RAG API is running"
    }


# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    result = answer_question(
        request.question
    )

    return ChatResponse(
        answer=result["answer"],
        confidence_label=result["confidence_label"],
        reason_code=result["reason_code"]
    )