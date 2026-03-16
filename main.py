from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

app = FastAPI(title="FastAPI Memory API", version="1.0.0")

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# メモリストレージ（簡易版）
class MemoryStore:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    def create_session(self, session_id: str, metadata: Optional[Dict] = None):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "metadata": metadata or {},
                "messages": []
            }
            self.conversations[session_id] = []
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        if session_id not in self.sessions:
            self.create_session(session_id)

        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.sessions[session_id]["messages"].append(message)
        self.conversations[session_id].append(message)
        return message

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def get_conversation(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        return self.conversations.get(session_id)

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["messages"] = []
            self.conversations[session_id] = []
        return {"status": "cleared"}

    def delete_session(self, session_id: str):
        self.sessions.pop(session_id, None)
        self.conversations.pop(session_id, None)
        return {"status": "deleted"}

    def list_sessions(self) -> List[str]:
        return list(self.sessions.keys())

memory = MemoryStore()

# モデル定義
class Message(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SessionCreate(BaseModel):
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    id: str
    metadata: Dict[str, Any]
    messages: List[Dict[str, Any]]

# エンドポイント定義
@app.get("/")
async def root():
    return {
        "message": "FastAPI Memory API",
        "version": "1.0.0",
        "endpoints": {
            "sessions": "/sessions",
            "messages": "/sessions/{session_id}/messages",
            "conversation": "/sessions/{session_id}/conversation"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate):
    return memory.create_session(session.session_id, session.metadata)

@app.get("/sessions", response_model=List[str])
async def list_sessions():
    return memory.list_sessions()

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    session = memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def add_message(session_id: str, message: Message):
    if session_id not in memory.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return memory.add_message(session_id, message.role, message.content, message.metadata)

@app.get("/sessions/{session_id}/conversation", response_model=List[Dict[str, Any]])
async def get_conversation(session_id: str):
    conversation = memory.get_conversation(session_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return conversation

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    if session_id not in memory.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return memory.clear_session(session_id)

@app.delete("/sessions/{session_id}/delete")
async def delete_session(session_id: str):
    if session_id not in memory.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return memory.delete_session(session_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
