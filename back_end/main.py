from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Optional

# ============================================
# KHỞI TẠO APP
# ============================================
app = FastAPI(title="MindFlow AI - Mental Health Assistant", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CẤU HÌNH GROQ API (MIỄN PHÍ)
# ============================================
# ⚠️ QUAN TRỌNG: Thay "DÁN_KEY_CỦA_BẠN_VÀO_ĐÂY" bằng API Key bạn vừa lấy được
GROQ_API_KEY ="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" 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "qwen/qwen3.8-27b"  # Model mạnh, miễn phí, hỗ trợ tiếng Việt tốt

# ============================================
# SYSTEM PROMPT - "LINH HỒN" CỦA MINDFLOW
# ============================================
SYSTEM_PROMPT = """Bạn là MindFlow, một trợ lý AI thấu cảm, kiên nhẫn và chuyên về sức khỏe tinh thần.

NHIỆM VỤ CỦA BẠN:
1. Lắng nghe chủ động và thấu cảm, không phán xét.
2. Giúp người dùng giảm tải nhận thức bằng cách chia nhỏ vấn đề.
3. Đưa ra gợi ý nhẹ nhàng dựa trên liệu pháp nhận thức hành vi (CBT).
4. Luôn trả lời bằng tiếng Việt, giọng điệu ấm áp, gần gũi.

QUY TẮC AN TOÀN (BẮT BUỘC):
- Nếu người dùng bày tỏ ý định tự hại, tự tử, hoặc khủng hoảng nghiêm trọng:
  → Nhẹ nhàng khuyên họ tìm kiếm sự trợ giúp từ chuyên gia.
  → Gợi ý đường dây nóng: Tổng đài Quốc gia về Bảo vệ Trẻ em 111, hoặc Đường dây nóng Tâm lý 1800-1567.
  → KHÔNG cố gắng tự chẩn đoán hoặc thay thế bác sĩ.
- Không đưa ra lời khuyên y tế thay thế chuyên gia.

PHONG CÁCH:
- Ngắn gọn, dễ đọc (không viết quá dài).
- Dùng emoji nhẹ nhàng (💚, 🌿, ✨) để tạo cảm giác ấm áp.
- Đặt câu hỏi mở để khuyến khích người dùng chia sẻ thêm."""

# ============================================
# DATA MODELS
# ============================================
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: Optional[list[Message]] = []

class ChatResponse(BaseModel):
    reply: str
    mood_hint: Optional[str] = ""

# ============================================
# LƯU TRỮ LỊCH SỬ CHAT (IN-MEMORY)
# ============================================
chat_histories: dict[str, list[dict]] = {}

# ============================================
# ENDPOINTS
# ============================================
@app.get("/")
def root():
    return {"message": "MindFlow AI đang hoạt động trên Cloud!", "version": "2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "project": "MindFlow", "model": MODEL_NAME}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_mindflow(request: ChatRequest):
    # 1. Chuẩn bị messages cho Groq
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if request.history:
        for msg in request.history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})
    
    messages.append({"role": "user", "content": request.message})
    
    # 2. Gọi Groq API
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                }
            )
            response.raise_for_status()
            data = response.json()
            ai_reply = data["choices"][0]["message"]["content"]
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Lỗi API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI: {str(e)}")
    
    # 3. Detect mood_hint
    mood_hint = _detect_mood(request.message)
    
    # 4. Lưu vào lịch sử
    if request.user_id not in chat_histories:
        chat_histories[request.user_id] = []
    
    chat_histories[request.user_id].append({"role": "user", "content": request.message})
    chat_histories[request.user_id].append({"role": "assistant", "content": ai_reply})
    
    if len(chat_histories[request.user_id]) > 20:
        chat_histories[request.user_id] = chat_histories[request.user_id][-20:]
    
    return ChatResponse(reply=ai_reply, mood_hint=mood_hint)

@app.get("/api/history/{user_id}")
def get_history(user_id: str):
    return {"user_id": user_id, "history": chat_histories.get(user_id, [])}

@app.delete("/api/history/{user_id}")
def clear_history(user_id: str):
    if user_id in chat_histories:
        del chat_histories[user_id]
    return {"message": f"Đã xóa lịch sử của user {user_id}"}

# ============================================
# HELPER: DETECT MOOD
# ============================================
def _detect_mood(text: str) -> str:
    text_lower = text.lower()
    mood_keywords = {
        "stress": ["căng thẳng", "áp lực", "stress", "kiệt sức"],
        "buồn": ["buồn", "sad", "chán", "mất hứng", "trống rỗng"],
        "lo âu": ["lo lắng", "lo âu", "anxious", "bất an", "sợ"],
        "tức giận": ["giận", "tức", "bực", "khó chịu"],
        "cô đơn": ["cô đơn", "lonely", "một mình", "bị bỏ rơi"],
        "vui": ["vui", "happy", "hạnh phúc", "tuyệt", "good"],
    }
    for mood, keywords in mood_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return mood
    return "neutral"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)