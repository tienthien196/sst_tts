# main.py
# TTS-AI Core API - Cung cấp dịch vụ Text-to-Speech và AI Text Generation
# Dùng: FastAPI + gTTS + QwenAIChatbot
import uvicorn
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import time
import logging

from gtts import gTTS
from pydantic import BaseModel

# Giả sử bạn đã có QwenAIChatbot trong qwenAI.py
from qwenAI import QwenAIChatbot

# === Cấu hình (thay bằng của bạn) ===
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyMjI4MGU2LTRkNzctNDI2NC05ZmI4LTg1NWYzYTJiMmJmMyIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTc1NzMxNzZ9.2cbHLMtwIt84kbJ8PMmVPr1KGkn-cfGYlscfQgb5uHU"
COOKIE = "cna=taRNIL78HkgCATq6MFcYSPOb; _bl_uid=vFmC58044yCjg4cjat9gk3Rss1Iy; visitor_id=ef774ac6e22316d4da1182628e661228; cnaui=422280e6-4d77-4264-9fb8-855f3a2b2bf3; aui=422280e6-4d77-4264-9fb8-855f3a2b2bf3; _gcl_au=1.1.1328138642.1756634692; xlly_s=1; acw_tc=0a03e54a17569683746562363e1e9aeadafd64cacb7e0a689c5172ad72bfab; x-ap=ap-southeast-1; sca=c3703b46; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyMjI4MGU2LTRkNzctNDI2NC05ZmI4LTg1NWYzYTJiMmJmMyIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTc1NzMxNzZ9.2cbHLMtwIt84kbJ8PMmVPr1KGkn-cfGYlscfQgb5uHU; atpsida=662a9635cc123d7e8eddde5d_1756968439_2; tfstk=gRhqkm48lId2YsIWG0FNzsWfJnFYQ5-BifZ_SV0gloqDDfNaSuuNcxgsS5RaqcEcj5YxrlztYs20mdFN_uahsZvxo57u5Dwcn1vOq84EXA10ssXNkboF1stvHVfa15xBABOIkqNTsH9yRm05DP4OICaci_VY5yaNRMRIkqQoeVDZkB_wtyjcnlmgn8juku40S-XDz74bo5f0IsXlquUgs520IT4uJPIGjsXDz4q87rVgjlYzZuUaslmgsUuoQargA_zUnUoxK8wFNe4YxqqPs6SJNRqeyra8qbJaIl0mgCAMWry4xqqymUABU80TQfQO_RgmpcUnmixaXbuoivmHVtZmLPuIQDY1HzwZM7riiBQUqjuZa-H5mt4Ugoyni-7BJqeiUbPjihBKP4r0L7MWenw_gmkLv-vJ2cuzccc4Ei-7fvgSi8oHV_oTQAcbZjxkTg5fXzXJ_fHVjOy0yzrBzUuClKBIZJDCgOBTHYUzAELABOe0yzrBzUWOB-F8zkTvk; isg=BBwcuUSWmJbFwWM1ELvDMuZA7TrOlcC_5yBXavYW74OVQa_PqaTATa23obG5SfgX; ssxmod_itna=CqGxuDnDcD2GlDeKqmq0K3uDek0DRlxBP01Dp6xQ5DODLxnR5GdKRGL+i37FDB7Q04qdKermbtDl2ihYD9xY6HDj4GT+zhBqhCF3nA2RNqRmThxdoMOxrRxYYmew+m2wuniNcFAwN1XheOeDU43DCuGr4eGGf4GwDGoD34DiDDPDbRiDAueD7qDFAWutZnbDm4GWKPDgG3PWHPDjQhb5O=4DGqDnG4G2bgb4DDN4QIDej7rdFPD+G+aTl1Tq8IxKAnEWDBdP9ID3upkXoinIL/SWTRrDzw1Dtuu8cnHOUmnNTa09/DxrBSqZieZ2DQA5WDtA2sQGDW0D3DxZ7DKDGxh4OYG=ls+DoQ7wDDfCiDNz=x2p57xrntBoXrOASo4xtmSiTMY4GlxdiG1Y2tfr10wq+KPihrindGGxlxPQ4DbxxD; ssxmod_itna2=CqGxuDnDcD2GlDeKqmq0K3uDek0DRlxBP01Dp6xQ5DODLxnR5GdKRGL+i37FDB7Q04qdKerm+YDipMw4r3Scq03=5Yahh1dD054EemfhR9hbsOr896FsOi3+zm=uYQqKmE5d6+6KiyzXUWBLni7LNiu=c/Gf0jGG6DuL5mu=e/ALKaut4TDXtgu=S7AvM7mtNNZ62K1agDTx/DMPS9OdDwhrNNujNDT=ZnqBxVci8EBfDEaWWgMPmO7iGOQrq1dr/i9L=ht0NS9TLjCQ0DuUB8k9EUl9N+9QdncOYISPemltMrzgy0m9gzu13HVK0FiK7ADMznGWD4ePxDhxUcM+rEW9sbG+Bq4lRd+pWKDP+w5mRw3nFj0GiGBBTibuS0WWA+lSTLle1mn7nwm/GeEPwBg6lRXC9Gip2WPqY0lDcexA4laMiD8WGa/03=F3vT+3Y6SY8DhP+eD=07CqGQ01GivQpa/pEiuXmBxTqmCuX0niX+hDSaGWzAwNza87PO2etsOM/xl4T4uHaTqHXcPDEUlONj+oxR6bdaiIxlyaERWQDm+x1SERCH79F/Dr7/pE64EZErraH6+KbwVl+by6iqw+e77Aoj+l76jTcaH6nkm1R9P89I7xnEin7rpNOn9QZ9V6mzwT8R3u2AbMWKRWKGeZ6KYGmY4hyQvDxPjRWEwZowgbLAC77WGdG47PuTyCDyG47N/ux7=2hw3pNrq7i503bAZqmSx0DrRjM2N/mbdy/NdDtUiq0NU+x0ACQc3MAfWQBiDrBDD=o8Eed=DTYDFEj0qYr5dY40iGAZwY6wYgXRrmmQWwGQ5pPKieKXxiKEbp4onxzA5b0W+4KxAn3smCB3r44iDD"

MODEL = "qwen3-235b-a22b"

# Khởi tạo bot AI
try:
    chatbot = QwenAIChatbot(auth_token=AUTH_TOKEN, cookie=COOKIE, model=MODEL)
except Exception as e:
    print(f"[ERROR] Không thể khởi tạo QwenAIChatbot: {e}")
    chatbot = None

# === Khởi tạo FastAPI ===
app = FastAPI(
    title="TTS-AI Core API",
    description="Dịch vụ Text-to-Speech và AI Text Generation. Dùng cho các hệ thống bên ngoài.",
    version="1.0.0",
    docs_url="/",  # Swagger UI tại /
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi nguồn (thay bằng domain cụ thể khi deploy)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts-ai-core")

# === Models ===
class TextRequest(BaseModel):
    text: str
    lang: str = "vi"  # Mặc định tiếng Việt

class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 512


# === API Endpoints ===

@app.get("/health")
def health_check():
    """Kiểm tra trạng thái API"""
    return {
        "status": "healthy",
        "service": "TTS-AI Core",
        "timestamp": int(time.time()),
        "qwen_connected": chatbot is not None
    }

@app.post("/tts")
async def text_to_speech(request: TextRequest):
    """
    Chuyển văn bản thành file âm thanh MP3
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text không được để trống")

    if request.lang not in ["vi", "en", "ja", "ko", "zh", "fr", "es"]:
        raise HTTPException(status_code=400, detail="Ngôn ngữ không hỗ trợ")

    # Tạo file tạm
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()

    try:
        tts = gTTS(text=request.text, lang=request.lang, slow=False)
        tts.save(temp_file.name)

        logger.info(f"TTS thành công: {len(request.text)} ký tự, ngôn ngữ={request.lang}")

        # ✅ Sửa: Dùng BackgroundTasks đúng cách
        background = BackgroundTasks()
        background.add_task(os.unlink, temp_file.name)

        return FileResponse(
            path=temp_file.name,
            media_type="audio/mpeg",
            filename="speech.mp3",
            background=background
        )

    except Exception as e:
        logger.error(f"Lỗi TTS: {str(e)}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise HTTPException(status_code=500, detail=f"TTS lỗi: {str(e)}")

@app.post("/ask")
async def ask_ai(request: PromptRequest):
    """
    Gửi prompt đến Qwen AI và nhận phản hồi text
    """
    if not chatbot:
        raise HTTPException(status_code=503, detail="AI backend không khả dụng")

    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt không được để trống")

    try:
        response = chatbot.get_ai_response(request.prompt)
        logger.info(f"AI response: {len(response)} ký tự")
        return {"text": response.strip()}
    except Exception as e:
        logger.error(f"Lỗi khi gọi Qwen API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI lỗi: {str(e)}")


# === Chạy server (python main.py) ===
if __name__ == "__main__":
    
    logger.info("🚀 Khởi động TTS-AI Core API tại http://localhost:8000")
    uvicorn.run("coreTTS:app", host="0.0.0.0", port=8000, reload=False)