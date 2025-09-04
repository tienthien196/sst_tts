import requests
import json
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
import os

console = Console()
class QwenAIChatbot:
    def __init__(self, auth_token, cookie, model="qwen3-235b-a22b", chat_id=None):
        self.url = "https://chat.qwen.ai/api/chat/completions" 
        self.auth_token = auth_token
        self.cookie = cookie
        self.model = model
        self.chat_id = chat_id or "14fd4efe-0a2c-4c23-8d71-d0f71102dd43"
        self.console = Console()
        self.full_content = ""
        self.messages = []

        # Chuẩn hóa headers
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "",  # tắt nén để dễ xử lý
            "authorization": self.auth_token,
            "content-type": "application/json",
            "Cookie": self.cookie.replace("…", "..."),
            "User-Agent": "Mozilla/5.0 Gecko/20100101 Firefox/139.0",
            "Referer": "https://chat.qwen.ai/c/d3eea510-c462-4579-8688-89803bde7025", 
            "source": "web",
            "version": "0.0.110",
            "bx-umidtoken": "T2gABB9f-lh8Kqjta5wZLGiZBYFcu0-PTnVOVGY8zHBzWgOalS8AWwzW2zTjYyIB0Cw=",
            "bx-ua": "231!Bc/3XkmUbkz+jmVDl+7MQFzjUAi2iSMytcZQLXn6+C0XJCxJxYn/VrKcqb5BcNTdnJLgnPK2nDd/1D2Nrnbj473fNUzFxQPTwjoyfYD8fd7ew08Sfx9/BAFDJ2dn6tAD569rIV9B1lJNSmsODAYRxKekLbupfSBvrbE62h3h5vpnmcdtqVgrwxBpR0xU4dXDTEd24O5bYF+nMnjL5gQGnWd3fboHTZUx6OoXiFop6vANwOsRnhjJ3v1Z+Sx+7PCtPfoz7EfFwF+V+WAt8wN2Ey/EALMxWOrrv7Er+MnepkDok+I9xGdFGnK/pglCok+++4mWYi++6Pg/jOeByUBDj+hG4bqIvOE88Okx3X7wyMzUwDGcJiewl3HIfkimRtqNUOhFQEIbwX16h78YYdq9wEU9LqR4GsHDSiSJNISACeARP6o6RcKxvdPGhpV6CLiJ8VNMgMyjrbRdbiuSHo5Vt7zRY2XjjARalJbNRmAwIvwUhW6jx2KmZLWSPbS9pbEmfZ0ODDLSGRykM/7Cj6xuK0WFwFYgzmr6ZYWbmAZUjnP82arx0l1dYWbXVAGHSSw8Pdk4ud4dFVNB1yXQGjafpWRtgur/xNiHZqJPyBaVET0UD+OCX3emzjx3x6GawOIycAEzFWMDxmi63iV7Q0Pcv4q4pdS5EVGoIbXxBf43Ety65Sl/mY49UujfaSBLqpF3n0v11LD8NYQHeVnBQeHbpmc4CK6pcN2u5iXZMhdc+wbzqbuXjhxKLWo2VPnRslldhso3ygZB4yKAGZFpD6ZdqTtM2/lc/yMnLZ5Vy1D9Xy9cnk48bXn148Ml3pZw0b382pM4JQCxMwjvCxuWrB1MFJSwDpd1TcgaxSJd9lQwMTpDJIIClZyfDu7L5crXvnn1XEYS5YbyIIooOTSedWhtsE/YN7LMjkCL81pos5e5iiiLyUcn9jj639ynO1FT/MVeWxdXgDE8lhWhYeMatA4rBF/Erp/LthstXaU4V7v8M9H+d7uDSw1Pxh86A==",
            "x-request-id": "41c6e8c4-6281-4353-afbd-c1rfab81e7c6",
        }

        # Cố định các giá trị header quan trọng
        self.headers["Cookie"] = self.headers["Cookie"].replace("…", "...")
        self.headers["bx-ua"] = self.headers["bx-ua"].replace("…", "...")

    def add_message(self, role, content):
        """Thêm một tin nhắn vào lịch sử"""
        self.messages.append({
            "role": role,
            "content": content
        })

    def send_query(self, user_input):
        """Gửi truy vấn đến API và nhận phản hồi"""
        self.add_message("user", user_input)

        data = {
            "chat_id": self.chat_id,
            "chat_mode": "normal",
            "chat_type": "t2t",
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "incremental_output": True
        }

        with self.console.status("[bold green]Đang nhận phản hồi từ AI...", spinner="dots") as status:
            with requests.post(self.url, headers=self.headers, json=data, stream=True) as response:
                if response.status_code == 200:
                    assistant_content = ""  # Biến tạm chỉ chứa nội dung của AI trong phiên này

                    panel = Panel("", title="Trả lời từ AI", border_style="blue", expand=False)

                    with Live(panel, refresh_per_second=10) as live:
                        for line in response.iter_lines():
                            if not line:
                                continue

                            try:
                                decoded_line = line.decode('utf-8').strip()
                            except UnicodeDecodeError:
                                continue

                            if decoded_line.startswith("data:"):
                                json_str = decoded_line[5:].strip()

                                if json_str == "[DONE]":
                                    # Sau khi hoàn tất, mới thêm vào messages
                                    self.messages[-1]["content"] = assistant_content
                                    break

                                try:
                                    parsed = json.loads(json_str)
                                    content = parsed["choices"][0]["delta"].get("content", "")
                                    if content:
                                        assistant_content += content
                                        live.update(Panel(Markdown(assistant_content), title="Trả lời từ AI", border_style="blue"))
                                except (json.JSONDecodeError, IndexError, KeyError):
                                    continue

                    # Thêm tin nhắn của AI vào messages sau khi hoàn tất
                    self.messages.append({
                        "role": "assistant",
                        "content": assistant_content
                    })

                    self.console.print(Panel("[green]✅ Hoàn tất[/]", border_style="green"))
                else:
                    self.console.print(
                        Panel(
                            f"[red]Lỗi {response.status_code}: {response.text}[/]",
                            title="Lỗi phản hồi",
                            border_style="red"
                        )
                    )

    def save_history(self, filename=r"C:\Users\ASUS\src\python\chat_history.json"):
        """Lưu lịch sử trò chuyện vào file JSON"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            self.console.print(f"[green]✅ Đã lưu lịch sử trò chuyện vào '{filename}'[/]")
        except Exception as e:
            self.console.print(f"[red]❌ Lỗi khi lưu file: {e}[/]")

    def load_history(self, filename=r"C:\Users\ASUS\src\python\chat_history.json"):
        """Tải lịch sử trò chuyện từ file JSON"""
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read().strip()  # Đọc và loại bỏ khoảng trắng đầu/cuối

                if not content:
                    self.console.print(f"[yellow]⚠️ File '{filename}' trống. Bắt đầu với lịch sử mới.[/]")
                    self.messages = []
                    return

                # Thử parse JSON
                self.messages = json.loads(content)
                self.console.print(f"[green]✅ Đã tải lịch sử trò chuyện từ '{filename}'[/]")

            except json.JSONDecodeError as e:
                self.console.print(f"[red]❌ File '{filename}' không phải định dạng JSON hợp lệ. Đặt lại lịch sử...[/]")
                self.messages = []

            except Exception as e:
                self.console.print(f"[red]❌ Lỗi khi đọc file: {e}[/]")
                self.messages = []
        else:
            self.console.print(f"[yellow]⚠️ Không tìm thấy file '{filename}'[/]")
            self.messages = []
# === Ví dụ sử dụng ===

    def get_ai_response(self, user_input):
        """
        Gửi truy vấn đến AI và trả về kết quả đầy đủ dưới dạng string
        """
        temp_messages = self.messages.copy()  # Lưu tạm lịch sử hiện tại
        temp_messages.append({
            "role": "user",
            "content": user_input
        })

        data = {
            "chat_id": self.chat_id,
            "chat_mode": "normal",
            "chat_type": "t2t",
            "model": self.model,
            "messages": temp_messages,
            "stream": True,
            "incremental_output": True
        }

        assistant_content = ""

        with requests.post(self.url, headers=self.headers, json=data, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        decoded_line = line.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        continue

                    if decoded_line.startswith("data:"):
                        json_str = decoded_line[5:].strip()

                        if json_str == "[DONE]":
                            break

                        try:
                            parsed = json.loads(json_str)
                            content = parsed["choices"][0]["delta"].get("content", "")
                            if content:
                                assistant_content += content
                        except (json.JSONDecodeError, IndexError, KeyError):
                            continue

            else:
                return f"Lỗi {response.status_code}: {response.text}"

        return assistant_content.strip()


    def stream_ai_response(self, user_input):
        temp_messages = self.messages.copy()
        temp_messages.append({
            "role": "user",
            "content": user_input
        })

        data = {
            "chat_id": self.chat_id,
            "chat_mode": "normal",
            "chat_type": "t2t",
            "model": self.model,
            "messages": temp_messages,
            "stream": True,
            "incremental_output": True
        }

        assistant_content = ""

        with requests.post(self.url, headers=self.headers, json=data, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        decoded_line = line.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        continue

                    if decoded_line.startswith("data:"):
                        json_str = decoded_line[5:].strip()

                        if json_str == "[DONE]":
                            break

                        try:
                            parsed = json.loads(json_str)
                            content = parsed["choices"][0]["delta"].get("content", "")
                            if content:
                                assistant_content += content
                                yield content  # Trả từng phần nhỏ
                        except (json.JSONDecodeError, IndexError, KeyError):
                            continue