from email.mime import text
import os
import sys, math, re, json, threading
import time
import threading
import json
import webbrowser

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QFrame, QScrollArea, QLineEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, QSize, QTimer, Signal, QPointF
from PySide6.QtGui import QIcon, QColor, QFont, QPainter, QPen, QPainterPath

from audio.recorder import VoiceRecorder
from brain.llm_handler import summarize_search, detect_intent, chat_response
from tts.piper_handler import speak
from actions.system_control import open_website
from memory.memory_handler import set_memory, update_context
from stt.voice_input import speech_to_text
from brain.llm_handler import detect_intent, chat_response


# ======================================================
# Waveform Widget
# ======================================================
class AudioWaveform(QWidget):
    def __init__(self):
        super().__init__()
        self.values = [0] * 40
        self.setFixedHeight(60)

    def update_level(self, level):
        self.values.append(level)
        self.values.pop(0)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width() / len(self.values)
        mid = self.height() / 2

        pen = QPen(QColor(192, 132, 252))
        ring_size = min(self.width(), self.height())

        if ring_size < 60:
            pen.setWidth(1)
        else:
            pen.setWidth(3)

        p.setPen(pen)

        for i, v in enumerate(self.values):
            x = i * w
            p.drawLine(QPointF(x, mid - v), QPointF(x, mid + v))


# ======================================================
# Neon Swirl Ring
# ======================================================
class NeonSwirlRing(QWidget):
    """Organic pulsing rings for AI and User State"""
    def __init__(self, color_hex):
        super().__init__()
        self.color = QColor(color_hex)
        self.phase = 0.0
        self.active = False
        self.listening = False

        self.setFixedSize(140, 140)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        self.timer.start(16)

    def set_active(self, state):
        self.active = state

    def set_listening(self, state):
        self.listening = state

    def step(self):
        self.phase += 0.08 if self.active else 0.03
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width()/2, self.height()/2

        amp = 0.4 if self.listening else 0.25
        cx, cy = self.width() / 2, self.height() / 2
        base_r = 42

        for t in range(2):
            path = QPainterPath()
            offset = self.phase + (t * 2)
            max_radius = min(self.width(), self.height()) / 2 - 4
            base_r = max_radius - 6
            amp = 2 if not self.active else 4

            for i in range(90):
                angle = (math.pi * 2 / 90) * i
                r = base_r + math.sin(angle * 3 + offset) * amp
                x = cx + math.cos(angle) * r
                y = cy + math.sin(angle) * r
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()

            for width, alpha in [(10, 20), (5, 50), (2, 255)]:
                c = QColor(self.color)
                c.setAlpha(alpha)
                p.setPen(QPen(c, width))
                p.drawPath(path)


# ======================================================
# Chat Bubble
# ======================================================
class ChatBubble(QFrame):
    """Modern messaging bubbles with gradients."""
    def __init__(self, text, is_user):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setFont(QFont("Segoe UI", 11))
        layout.addWidget(lbl)

        if is_user:
            self.setStyleSheet("background:#312e81; color:#f5f3ff; border-radius:15px; border-bottom-right-radius:2px;")
        else:
            self.setStyleSheet("background:#0f172a; color:#e2e8f0; border:1px solid #1e293b; border-radius:15px; border-bottom-left-radius:2px;")

#========================================================
# Thinking Animation 
#========================================================
class ThinkingBubble(QFrame):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        self.ring = NeonSwirlRing("#818cf8")
        self.ring.setFixedSize(24, 24)
        self.ring.set_active(True)

        lbl = QLabel("Thinking...")
        lbl.setStyleSheet("color:#e2e8f0;")
        lbl.setFont(QFont("Segoe UI", 10))

        layout.addWidget(self.ring)
        layout.addWidget(lbl)

        self.setStyleSheet("""
            background:#0f172a;
            border:1px solid #1e293b;
            border-radius:15px;
            border-bottom-left-radius:2px;
        """)

# =======================================================
# MAIN GUI
# =======================================================
class ImageMicButton(QPushButton):
    def __init__(self, idle_path, active_path, size=50):
        super().__init__()

        # 1. Setup Button Styles
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

        # 2. Load Icons
        self.icon_idle = QIcon(idle_path)
        self.icon_active = QIcon(active_path)

        # Debugging helper
        if not os.path.exists(idle_path):
            print(f"WARNING: Could not find image at {idle_path}")
        if not os.path.exists(active_path):
            print(f"WARNING: Could not find image at {active_path}")

        # 3. Set Default State
        self.setIcon(self.icon_idle)
        self.setIconSize(QSize(size, size))

    def set_recording(self, is_recording):
        self.setIcon(self.icon_active if is_recording else self.icon_idle)


class ChaseGUI(QWidget):


    def show_thinking(self):
      self.thinking_row = QWidget()
      row_layout = QHBoxLayout(self.thinking_row)
      row_layout.setContentsMargins(0, 5, 0, 5)

      bubble = ThinkingBubble()

      row_layout.addWidget(bubble)
      row_layout.addStretch()

      self.chat_layout.addWidget(self.thinking_row)

      QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
      self.scroll.verticalScrollBar().maximum()
    ))

    def handle_send(self):
        text =self.input.text().strip()

        if not text:
            return
        
        self.add_message(text, is_user=True)
        self.input.clear()

        self.add_message("Thinking...", is_user=False)

        # Detect intent
        intent_raw = detect_intent(text)

        try:
            intent_data = json.loads(intent_raw)
            intent = intent_data.get("intent")
            target = intent_data.get("target", "").lower().strip()

        except Exception:
            intent = "unknown"
            target = ""
               
        # Router
        if intent == "open_website":
            webbrowser.open("https://{target}.com")
            self.add_message(f"Opening {target}.", is_user=False)

        elif intent == "open_application":
            os.system(target)
            self.add_message(f"Opening {target}.", is_user=False)
            target = target.replace(".","")

        else:
            #Normal chat
            reply = chat_response(text)
            self.add_message(reply, is_user=False)      


      
    def process_llm(self, text):
     try:
        reply = chat_response(text)

        # Remove last "Thinking..." bubble
        if hasattr(self, "thinking_row"):
            self.thinking_row.setParent(None)

        self.add_msg_signal.emit(reply, False)

     except Exception as e:
        print("LLM ERROR:", e)
        self.add_msg_signal.emit("Error: LLM failed.", False)


    add_msg_signal = Signal(str, bool)  # (text, is_user)
    status_sig = Signal(str)  # For updating input placeholder during recording/processing

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chase")
        self.setMinimumSize(550, 850)
        self.setStyleSheet("background-color: #020617;")
        self.is_recording = False

        self.init_UI()

        # Connect Signals
        self.add_msg_signal.connect(self.add_message)
        self.status_sig.connect(lambda s: self.input_field.setPlaceholderText(s))

        # Placeholder for external modules
        # self.recorder = VoiceRecorder(self.waveform.update_level)

    def init_UI(self):
         self.setWindowTitle("Chase Assistant")
         self.setMinimumSize(1000, 650)
         self.setStyleSheet("background-color: #0b1020;")

         self.main_layout = QVBoxLayout(self)
         self.main_layout.setContentsMargins(40, 30, 40, 30)
         self.main_layout.setSpacing(20)

    # ================= HEADER =================
         self.header_container = QWidget()
         header_layout = QHBoxLayout(self.header_container)

         self.header_logo = NeonSwirlRing("#818cf8")
         self.header_logo.setFixedSize(36, 36)
         header_layout.addWidget(self.header_logo)
         header_layout.addStretch()
         
         self.header_container.hide()
         self.main_layout.addWidget(self.header_container)

    # ================= HERO SECTION =================
         self.hero_container = QWidget()
         hero_layout = QVBoxLayout(self.hero_container)
         hero_layout.setAlignment(Qt.AlignCenter)

         self.hero_ring = NeonSwirlRing("#818cf8")

         self.hero_title = QLabel("How can I help you?")
         self.hero_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
         self.hero_title.setStyleSheet("color: white;")
         self.hero_title.setAlignment(Qt.AlignCenter)

         hero_layout.addWidget(self.hero_ring, alignment=Qt.AlignCenter)
         hero_layout.addSpacing(20)
         hero_layout.addWidget(self.hero_title)

         self.main_layout.addWidget(self.hero_container, stretch=1)

    # ================= CHAT AREA =================
         self.scroll = QScrollArea()
         self.scroll.setWidgetResizable(True)
         self.scroll.setStyleSheet("border: none;")
         self.scroll.hide()

         self.chat_widget = QWidget()
         self.chat_layout = QVBoxLayout(self.chat_widget)
         self.chat_layout.setAlignment(Qt.AlignTop)
         self.chat_layout.setSpacing(15)

         self.scroll.setWidget(self.chat_widget)
         self.main_layout.addWidget(self.scroll, stretch=1)

    # ================= INPUT =================
         self.input_container = QFrame()
         self.input_container.setFixedHeight(50)
         self.input_container.setFixedWidth(460)
         self.input_container.setStyleSheet("""
             background-color: #1e293b;
             border-radius: 24px;
             border: 1px solid #2d3748;
         """)

         input_layout = QHBoxLayout(self.input_container)
         input_layout.setContentsMargins(20, 0, 20, 0)

         self.input = QLineEdit()
         self.input.setPlaceholderText("Ask anything...")
         self.input.setFont(QFont("Segoe UI", 11))
         self.input.setStyleSheet("""
              border: none;
              background: transparent;
              color: white;
          """)

         self.input.returnPressed.connect(self.handle_send)

         input_layout.addWidget(self.input)

    # Initially center input inside hero
         hero_layout.addSpacing(30)
         hero_layout.addWidget(self.input_container, alignment=Qt.AlignCenter)


    # ---------------- UI SAFE ----------------
    def add_message(self, text, is_user):

        if hasattr(self, "hero_container") and self.hero_container.isVisible():
            self.hero_container.hide()
            self.header_container.show()
            self.scroll.show()

            # Move input to bottom
            self.main_layout.addWidget(self.input_container)
            self.input_container.setMinimumWidth(0)
            self.input_container.setMaximumWidth(16777215)


        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 5, 0, 5)

        bubble = ChatBubble(text, is_user)

        if is_user:
            row_layout.addStretch()
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch()

        self.chat_layout.addWidget(row)

        # Auto-scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    # ---------------- MIC ----------------
    def toggle_mic(self):
        if not self.is_recording:
            self.is_recording = True
            self.input_field.setPlaceholderText("Recording… press Enter to send")
            self.user_ring.set_listening(True)
            if hasattr(self, "recorder") and self.recorder:
                self.recorder.start()
        else:
            self.send_voice()

    def send_voice(self):
        self.is_recording = False
        self.user_ring.set_active(False)
        self.mic_btn.setStyleSheet("background-color: #ef4444; border-radius: 20px;")
        self.status_sig.emit("Processing voice input…")

        audio = None
        if hasattr(self, "recorder") and self.recorder:
            audio = self.recorder.stop()

        if not audio:
            self.status_sig.emit("Ask anything...")
            return

        threading.Thread(
            target=self.process_voice,
            args=(audio,),
            daemon=True
        ).start()

    # ---------------- SEND ----------------
    def send_text(self):
        if self.is_recording:
            self.send_voice()
            return

        text = self.input_field.text().strip()
        self.input_field.clear()
        if not text:
            return

        self.add_msg_signal.emit(text, True)
        threading.Thread(target=self.process, args=(text,), daemon=True).start()

    def process(self, text):
        try:
            print("Processing:", text)

            reply = chat_response(text)

            print("LLM Reply:", reply)

            self.add_msg_signal.emit(reply, False)

        except Exception as e:
            print("LLM ERROR:", e)
            self.add_msg_signal.emit("Error: LLM failed.", False)
    

    def process_voice(self, audio):

        time.sleep(1)
        text = speech_to_text(audio)

        if text:
            self.input_field.setPlaceholderText("Type your message…")
            self.add_msg_signal.emit(text, True)
            self.process(text)

    # ---------------- LOGIC ----------------
    def process(self, user_input):
        clean = re.sub(r"[^\w\s]", "", user_input.lower())

        try:
            intent = json.loads(detect_intent(clean))
        except:
            self.reply(summarize_search(clean, ""))
            return

        if intent.get("intent") == "open_website" and "youtube" in intent.get("target", ""):
            self.reply("Opening YouTube.")
            open_website("https://youtube.com")
            update_context("last_app", "youtube")
            return

        time.sleep(0.5)
        response = summarize_search(clean, "")
        self.reply(response)

    def reply(self, message):
        self.add_message(message, is_user=False)
        # UI SAFE
        avater = NeonSwirlRing("#818cf8")
        avater.setFixedSize(28, 28)


# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set App Font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = ChaseGUI()
    win.show()
    sys.exit(app.exec())
