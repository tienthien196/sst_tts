# tts_exam_bot.py
# Trợ lý AI giao tiếp bằng giọng nói 2 chiều
# Micro → STT → Qwen AI → TTS → Tai nghe

import requests
import json
import os
import time
import random
import tempfile

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from gtts import gTTS  # Text-to-Speech
import pygame  # Phát âm thanh
import speech_recognition as sr  # Speech-to-Text

# Giả sử bạn đã lưu QwenAIChatbot trong file: qwenAI.py
from qwenAI import QwenAIChatbot

console = Console()


class TTSExamBot:
    def __init__(self, auth_token, cookie, model="qwen3-235b-a22b", chat_id=None):
        """
        Khởi tạo bot AI với TTS + STT
        """
        self.chatbot = QwenAIChatbot(auth_token=auth_token, cookie=cookie, model=model, chat_id=chat_id)
        self.console = Console()
        self.setup_audio()

    def setup_audio(self):
        """Khởi tạo pygame mixer cho TTS"""
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    def speak(self, text, lang='vi'):
        """
        Chuyển văn bản thành giọng nói và phát qua tai nghe
        """
        text = text.strip()
        if not text:
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            temp_filename = f.name

        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_filename)

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

        except Exception as e:
            self.console.print(f"[red]❌ Lỗi TTS: {e}[/]")
        finally:
            try:
                os.unlink(temp_filename)
            except:
                pass

    def listen(self, lang="vi-VN", timeout=5, phrase_time_limit=10):
        """
        Ghi âm từ micro và chuyển thành text (STT)
        :param lang: Ngôn ngữ (vi-VN, en-US, ...)
        :param timeout: Thời gian chờ âm thanh (s)
        :param phrase_time_limit: Thời gian tối đa nói 1 lần (s)
        :return: text hoặc None
        """
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            console.print("[yellow]🔊 Đang lắng nghe... (nói đi!)[/]")
            recognizer.adjust_for_ambient_noise(source)  # Tự động giảm ồn

            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                console.print("[green]✅ Đã nhận được âm thanh, đang xử lý...[/]")

                # Dùng Google Web Speech API (miễn phí, cần internet)
                text = recognizer.recognize_google(audio, language=lang)
                return text.strip()

            except sr.WaitTimeoutError:
                console.print("[orange]⏰ Hết thời gian chờ âm thanh.[/]")
            except sr.UnknownValueError:
                console.print("[orange]🤖 Không nghe rõ. Bạn nói lại được không?[/]")
            except sr.RequestError as e:
                console.print(f"[red]❌ Lỗi kết nối đến Google STT: {e}[/]")
            except Exception as e:
                console.print(f"[red]❌ Lỗi STT: {e}[/]")

            return None

    def chat_loop(self, max_turns=10):
        """
        Bắt đầu vòng lặp hội thoại 2 chiều bằng giọng nói
        """
        self.console.print(Panel("🎙️ [bold blue]Trợ lý AI: Sẵn sàng hội thoại bằng giọng nói![/]", expand=False))
        self.speak("Xin chào! Tôi là trợ lý AI. Hãy nói bất cứ điều gì bạn muốn.")

        for turn in range(max_turns):
            self.console.print(f"\n[bold cyan]Lượt {turn + 1}/{max_turns}[/]")

            # 1. Nghe người dùng nói
            user_text = self.listen(lang="vi-VN")  # Có thể đổi thành en-US nếu cần
            if not user_text:
                self.speak("Tôi không nghe rõ. Bạn thử lại nhé.")
                continue

            self.console.print(Panel(Markdown(f"**Bạn:** {user_text}"), border_style="blue"))

            # 2. Gửi đến AI
            try:
                ai_response = self.chatbot.get_ai_response(user_text)
                self.console.print(Panel(Markdown(f"**AI:** {ai_response}"), border_style="green"))

                # 3. Phát phản hồi của AI
                self.speak(ai_response, lang='vi')  # Có thể tự động phát hiện ngôn ngữ nếu cần

            except Exception as e:
                error_msg = "Xin lỗi, tôi không thể phản hồi ngay lúc này."
                self.console.print(f"[red]❌ Lỗi AI: {e}[/]")
                self.speak(error_msg)

        # Kết thúc
        goodbye = "Cảm ơn bạn đã trò chuyện. Tạm biệt!"
        self.console.print(Panel(goodbye, title="👋 Kết thúc", border_style="magenta"))
        self.speak(goodbye)

    def start_exam(self, num_questions=5):
        """
        (Giữ nguyên phần kiểm tra nếu bạn vẫn muốn dùng)
        """
        self.console.print(Panel("🎤 [bold blue]Chào mừng bạn đến với phần thi nhận thức![/]", expand=False))
        self.speak("Xin chào! Tôi là giám khảo AI. Hãy cùng bắt đầu bài kiểm tra nhận thức.")

        score = 0

        for i in range(num_questions):
            self.console.print(f"\n[bold cyan]Câu hỏi {i+1}/{num_questions}[/]")

            # Tạo câu hỏi
            qa = self.generate_question(difficulty=random.choice(["dễ", "trung bình", "khó"]))
            if not qa["question"] or not qa["answer"]:
                self.console.print("[yellow]⚠️ Không thể tạo câu hỏi, bỏ qua...[/]")
                self.speak("Không thể tạo câu hỏi. Chuyển sang câu tiếp theo.")
                continue

            self.current_question = qa["question"]

            # Hiển thị và đọc to
            self.console.print(Panel(Markdown(qa["question"]), title="❓ Câu hỏi", border_style="yellow"))
            self.speak(qa["question"])

            # 👉 Thay thế nhập text bằng STT
            user_answer = self.listen(lang="vi-VN")
            if not user_answer:
                user_answer = ""

            # Đánh giá
            is_correct = self.evaluate_answer(user_answer, qa["answer"])

            # Phản hồi
            if is_correct:
                score += 1
                feedback = "Chính xác! Câu trả lời của bạn hoàn toàn đúng."
                self.console.print("[green]✅ Chính xác![/]")
            else:
                feedback = f"Rất tiếc, câu trả lời chưa đúng. Đáp án đúng là: {qa['answer']}."
                self.console.print(f"[red]❌ Sai. Đáp án: {qa['answer']}[/]")

            self.console.print(feedback)
            self.speak(feedback)

        # Tổng kết
        final_msg = f"Bài kiểm tra kết thúc. Bạn đạt {score}/{num_questions} câu đúng."
        self.console.print(Panel(final_msg, title="🎯 Kết quả", border_style="green", padding=1))
        self.speak(final_msg)
        self.speak("Cảm ơn bạn đã tham gia phần thi nhận thức. Hẹn gặp lại!")

    # Các hàm hỗ trợ cũ (giữ nguyên)
    def generate_question(self, field=None, difficulty="trung bình"):
        if not field:
            fields = ["khoa học", "lịch sử", "công nghệ", "văn hóa", "toán học", "địa lý", "sinh học", "logic", "chính trị", "kinh tế"]
            field = random.choice(fields)

        prompt = (
            f"Bạn là một giám khảo thông minh. Hãy tạo một câu hỏi {difficulty} về lĩnh vực {field}, "
            f"kèm theo đáp án chính xác. Câu hỏi phải rõ ràng, phù hợp với người trưởng thành.\n\n"
            f"Định dạng:\n"
            f"Câu hỏi: [nội dung câu hỏi]\n"
            f"Đáp án: [đáp án đúng]"
        )
        try:
            response = self.chatbot.get_ai_response(prompt)
            return self.parse_question_answer(response)
        except Exception as e:
            self.console.print(f"[red]Lỗi khi tạo câu hỏi: {e}[/]")
            return {"question": "", "answer": ""}

    def parse_question_answer(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        question = ""
        answer = ""
        for line in lines:
            if line.startswith(("Câu hỏi:", "Câu hỏi")):
                question = line.split(":", 1)[1].strip()
            elif line.startswith(("Đáp án:", "Đáp án")):
                answer = line.split(":", 1)[1].strip()
        return {"question": question, "answer": answer}

    def evaluate_answer(self, user_answer, correct_answer):
        if not user_answer.strip():
            return False
        prompt = (
            "Bạn là giám khảo. Hãy đánh giá xem câu trả lời của người chơi có đúng với tinh thần đáp án không. "
            "Chỉ trả lời 'đúng' hoặc 'sai'.\n\n"
            f"Câu hỏi: {self.current_question}\n"
            f"Người chơi trả lời: {user_answer}\n"
            f"Đáp án đúng: {correct_answer}"
        )
        try:
            result = self.chatbot.get_ai_response(prompt).strip().lower()
            return "đúng" in result
        except:
            return correct_answer.lower() in user_answer.lower()


# === Token và chạy chương trình ===
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyMjI4MGU2LTRkNzctNDI2NC05ZmI4LTg1NWYzYTJiMmJmMyIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTc1NzMxNzZ9.2cbHLMtwIt84kbJ8PMmVPr1KGkn-cfGYlscfQgb5uHU"
COOKIE = "cna=taRNIL78HkgCATq6MFcYSPOb; _bl_uid=vFmC58044yCjg4cjat9gk3Rss1Iy; visitor_id=ef774ac6e22316d4da1182628e661228; cnaui=422280e6-4d77-4264-9fb8-855f3a2b2bf3; aui=422280e6-4d77-4264-9fb8-855f3a2b2bf3; _gcl_au=1.1.1328138642.1756634692; xlly_s=1; acw_tc=0a03e54a17569683746562363e1e9aeadafd64cacb7e0a689c5172ad72bfab; x-ap=ap-southeast-1; sca=c3703b46; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQyMjI4MGU2LTRkNzctNDI2NC05ZmI4LTg1NWYzYTJiMmJmMyIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTc1NzMxNzZ9.2cbHLMtwIt84kbJ8PMmVPr1KGkn-cfGYlscfQgb5uHU; atpsida=662a9635cc123d7e8eddde5d_1756968439_2; tfstk=gRhqkm48lId2YsIWG0FNzsWfJnFYQ5-BifZ_SV0gloqDDfNaSuuNcxgsS5RaqcEcj5YxrlztYs20mdFN_uahsZvxo57u5Dwcn1vOq84EXA10ssXNkboF1stvHVfa15xBABOIkqNTsH9yRm05DP4OICaci_VY5yaNRMRIkqQoeVDZkB_wtyjcnlmgn8juku40S-XDz74bo5f0IsXlquUgs520IT4uJPIGjsXDz4q87rVgjlYzZuUaslmgsUuoQargA_zUnUoxK8wFNe4YxqqPs6SJNRqeyra8qbJaIl0mgCAMWry4xqqymUABU80TQfQO_RgmpcUnmixaXbuoivmHVtZmLPuIQDY1HzwZM7riiBQUqjuZa-H5mt4Ugoyni-7BJqeiUbPjihBKP4r0L7MWenw_gmkLv-vJ2cuzccc4Ei-7fvgSi8oHV_oTQAcbZjxkTg5fXzXJ_fHVjOy0yzrBzUuClKBIZJDCgOBTHYUzAELABOe0yzrBzUWOB-F8zkTvk; isg=BBwcuUSWmJbFwWM1ELvDMuZA7TrOlcC_5yBXavYW74OVQa_PqaTATa23obG5SfgX; ssxmod_itna=CqGxuDnDcD2GlDeKqmq0K3uDek0DRlxBP01Dp6xQ5DODLxnR5GdKRGL+i37FDB7Q04qdKermbtDl2ihYD9xY6HDj4GT+zhBqhCF3nA2RNqRmThxdoMOxrRxYYmew+m2wuniNcFAwN1XheOeDU43DCuGr4eGGf4GwDGoD34DiDDPDbRiDAueD7qDFAWutZnbDm4GWKPDgG3PWHPDjQhb5O=4DGqDnG4G2bgb4DDN4QIDej7rdFPD+G+aTl1Tq8IxKAnEWDBdP9ID3upkXoinIL/SWTRrDzw1Dtuu8cnHOUmnNTa09/DxrBSqZieZ2DQA5WDtA2sQGDW0D3DxZ7DKDGxh4OYG=ls+DoQ7wDDfCiDNz=x2p57xrntBoXrOASo4xtmSiTMY4GlxdiG1Y2tfr10wq+KPihrindGGxlxPQ4DbxxD; ssxmod_itna2=CqGxuDnDcD2GlDeKqmq0K3uDek0DRlxBP01Dp6xQ5DODLxnR5GdKRGL+i37FDB7Q04qdKerm+YDipMw4r3Scq03=5Yahh1dD054EemfhR9hbsOr896FsOi3+zm=uYQqKmE5d6+6KiyzXUWBLni7LNiu=c/Gf0jGG6DuL5mu=e/ALKaut4TDXtgu=S7AvM7mtNNZ62K1agDTx/DMPS9OdDwhrNNujNDT=ZnqBxVci8EBfDEaWWgMPmO7iGOQrq1dr/i9L=ht0NS9TLjCQ0DuUB8k9EUl9N+9QdncOYISPemltMrzgy0m9gzu13HVK0FiK7ADMznGWD4ePxDhxUcM+rEW9sbG+Bq4lRd+pWKDP+w5mRw3nFj0GiGBBTibuS0WWA+lSTLle1mn7nwm/GeEPwBg6lRXC9Gip2WPqY0lDcexA4laMiD8WGa/03=F3vT+3Y6SY8DhP+eD=07CqGQ01GivQpa/pEiuXmBxTqmCuX0niX+hDSaGWzAwNza87PO2etsOM/xl4T4uHaTqHXcPDEUlONj+oxR6bdaiIxlyaERWQDm+x1SERCH79F/Dr7/pE64EZErraH6+KbwVl+by6iqw+e77Aoj+l76jTcaH6nkm1R9P89I7xnEin7rpNOn9QZ9V6mzwT8R3u2AbMWKRWKGeZ6KYGmY4hyQvDxPjRWEwZowgbLAC77WGdG47PuTyCDyG47N/ux7=2hw3pNrq7i503bAZqmSx0DrRjM2N/mbdy/NdDtUiq0NU+x0ACQc3MAfWQBiDrBDD=o8Eed=DTYDFEj0qYr5dY40iGAZwY6wYgXRrmmQWwGQ5pPKieKXxiKEbp4onxzA5b0W+4KxAn3smCB3r44iDD"

if __name__ == "__main__":
    if AUTH_TOKEN == "your_auth_token_here" or COOKIE == "your_cookie_string_here":
        console.print("[red]❌ Vui lòng thay thế AUTH_TOKEN và COOKIE bằng giá trị thật![/]")
    else:
        bot = TTSExamBot(auth_token=AUTH_TOKEN, cookie=COOKIE)

        # 🎯 Chọn chế độ:
        console.print("[bold]Chọn chế độ:[/]")
        console.print("1. [green]Chat bằng giọng nói liên tục (2 chiều)[/]")
        console.print("2. [yellow]Thi trắc nghiệm (dùng micro)[/]")

        choice = console.input("Nhập lựa chọn (1/2): ").strip()

        if choice == "1":
            bot.chat_loop(max_turns=10)  # Chat 10 lượt
        elif choice == "2":
            bot.start_exam(num_questions=5)
        else:
            console.print("[red]Lựa chọn không hợp lệ.[/]")