# doctor_bin_cli.py
# CLI Tool: Thầy Bin - Vị giáo sư hỏi xoáy từ A đến Á
# Sử dụng: TTS-AI Core API (localhost:8000)

import requests
import os
import time
import sys

# Cấu hình API
TTS_AI_API = "http://localhost:8000"

def speak_text(text, lang="vi"):
    """Phát giọng nói qua API TTS"""
    try:
        response = requests.post(f"{TTS_AI_API}/tts", json={"text": text, "lang": lang}, stream=True)
        if response.status_code == 200:
            # Phát âm thanh tạm
            with open("temp_speech.mp3", "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            os.system("start temp_speech.mp3")  # Windows
            # Trên Mac: os.system("afplay temp_speech.mp3")
            # Trên Linux: os.system("mpg321 temp_speech.mp3")

            # Chờ phát xong (ước lượng)
            time.sleep(len(text) / 15)  # Giả định tốc độ 15 chữ/giây
        else:
            print(f"[TTS Lỗi] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Lỗi phát âm] {e}")

def ask_ai(prompt):
    """Gửi câu hỏi đến AI qua API /ask"""
    try:
        response = requests.post(f"{TTS_AI_API}/ask", json={"prompt": prompt})
        if response.status_code == 200:
            return response.json().get("text", "").strip()
        else:
            return f"[AI Lỗi {response.status_code}] Không thể lấy phản hồi."
    except Exception as e:
        return f"[Lỗi kết nối] {str(e)}"

def main():
    print("🎤 [Thầy Bin AI] Khởi động... Xin chào, tôi là Tiến sĩ Bin – chuyên gia phỏng vấn đa lĩnh vực.")
    speak_text("Xin chào! Tôi là Tiến sĩ Bin. Hãy chuẩn bị tinh thần, vì tôi sẽ hỏi bạn từ A đến Á!")

    # Hỏi chủ đề
    print("\n📋 Bạn muốn bị hỏi về chủ đề gì? (ví dụ: AI, triết học, Python, vũ trụ, đạo đức học...)")
    topic = input("👉 Chủ đề: ").strip()
    if not topic:
        topic = "khoa học máy tính"

    # Mở đầu
    opening_prompt = f"""
Bạn là Tiến sĩ Bin – một giáo sư uyên bác, nghiêm khắc và thích đào sâu đến gốc rễ vấn đề.
Hãy đặt một câu hỏi mở đầu cực kỳ sâu sắc, hóc búa về chủ đề '{topic}',
để kiểm tra tư duy phản biện và kiến thức nền tảng của người học.
Câu hỏi phải khiến người nghe phải suy nghĩ thật lâu.
    """.strip()

    print("\n🧠 [Thầy Bin] Đang suy nghĩ...")
    question = ask_ai(opening_prompt)
    print(f"\n🎓 [Thầy Bin]: {question}")
    speak_text(question)

    # Vòng hỏi đáp liên tục
    for round_num in range(1, 6):  # 5 vòng
        print(f"\n💬 Bạn trả lời (hoặc gõ 'thoát' để kết thúc):")
        user_answer = input("👉 Trả lời: ").strip()
        if user_answer.lower() in ['thoát', 'quit', 'exit']:
            break

        # Thầy Bin phản biện hoặc hỏi tiếp
        follow_up_prompt = f"""
Bạn là Tiến sĩ Bin. Người học vừa trả lời: "{user_answer}" cho câu hỏi trước.
Hãy đưa ra phản biện sắc bén, chỉ ra điểm thiếu sót (nếu có),
rồi đặt một câu hỏi kế tiếp sâu hơn, khó hơn, liên quan đến gốc rễ vấn đề.
Hãy giữ phong cách nghiêm khắc, học thuật cao.
        """.strip()

        print(f"\n🧠 [Thầy Bin] Đang phản biện và đặt câu hỏi tiếp...")
        next_question = ask_ai(follow_up_prompt)
        print(f"\n🎓 [Thầy Bin]: {next_question}")
        speak_text(next_question)

    # Kết thúc
    closing = "Cảm ơn bạn đã trải qua buổi phỏng vấn với Tiến sĩ Bin. Bạn đã thể hiện tư duy, nhưng vẫn còn nhiều điều để đào sâu. Hãy tiếp tục học hỏi."
    print(f"\n🔚 {closing}")
    speak_text(closing)

    # Dọn dẹp
    if os.path.exists("temp_speech.mp3"):
        time.sleep(1)
        os.remove("temp_speech.mp3")

if __name__ == "__main__":
    main()