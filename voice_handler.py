# ------------------------ استيراد المكتبات المطلوبة ------------------------
from PyQt5.QtWidgets import QTextEdit, QPushButton
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor
import pyttsx3
import pyaudio
from vosk import Model, KaldiRecognizer
import json
import threading
import time
import sys




class VoiceHandler(QObject):
    text_recognized = pyqtSignal(str)
    listening_state_changed = pyqtSignal(bool)
    update_display_request = pyqtSignal(str)  # إشارة جديدة لتحديث العرض
    
    def __init__(self, chat_area, entry, button_voice, button_send):
        super().__init__()
        self.chat_area = chat_area
        self.entry = entry
        self.button_voice = button_voice
        self.button_send = button_send
        self.is_listening = False
        self.listening_flag = False
        self.last_activity_time = 0
        self.conversation_history = []
        
        # إعدادات التحكم
        self.trigger_words = {'تم', 'انتهيت', 'كفاية'}
        self.ending_punctuation = {'.', '؟', '!', '...'}
        self.max_silence = 5  # ثواني
        
        # تهيئة نموذج التعرف الصوتي
        self.model = Model(r"C:\Users\bassam\Desktop\bassam\vosk-model-ar-0.22-linto-1.1.0")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        
        # تهيئة محرك الصوت
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'arabic' in voice.languages or 'ar_' in voice.id:
                self.engine.setProperty('voice', voice.id)
                break
        
        # مؤقت الصمت
        self.silence_timer = QTimer()
        self.silence_timer.timeout.connect(self.check_silence)
        
        # ربط الإشارات
        self.update_display_request.connect(self.update_display_slot)

    @pyqtSlot(str)
    def update_display_slot(self, text):
        """تحديث مربع النص مع التمدد الذكي"""
        lines = text.split('\n')
        line_count = len(lines)
        
        # حساب الارتفاع المطلوب (بين 60 و150 بكسل)
        new_height = min(max(line_count * 25, 40),150)
        self.entry.setFixedHeight(new_height)
        
        # عرض النص مع الحفاظ على فواصل الأسطر
        self.entry.setPlainText(text)
        
        # التمرير إلى الأسفل
        cursor = self.entry.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.entry.setTextCursor(cursor)


    def update_current_line(self, text):
        """تحديث السطر الحالي مع الاحتفاظ بالجمل السابقة"""
        try:
            if self.conversation_history:
                display_text = "\n".join(self.conversation_history) + "\n" + text
            else:
                display_text = text
            
            self.update_display_request.emit(display_text)
        except Exception as e:
            print(f"Error updating current line: {str(e)}")

    def toggle_microphone(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.listening_flag = True
        self.listening_state_changed.emit(True)
        self.update_button_style(True)
        self.play_sound('start')
        
        # تفعيل مؤقت الصمت
        self.silence_timer.start(1000)
        
        # بدء التسجيل في thread منفصل
        threading.Thread(target=self.recording_loop, daemon=True).start()

    def recording_loop(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )

        try:
            while self.listening_flag:
                data = stream.read(4096, exception_on_overflow=False)
                self.process_audio(data)
                
        except Exception as e:
            self.chat_area.append(f"خطأ في التسجيل: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def process_audio(self, data):
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                self.handle_complete_sentence(text)
        else:
            partial = json.loads(self.recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            if partial_text:
                self.update_current_line(partial_text)
                self.last_activity_time = time.time()

    def handle_complete_sentence(self, text):
        self.conversation_history.append(text)
        self.update_display("\n".join(self.conversation_history))
        self.last_activity_time = time.time()
        
        if self.should_send(text):
            self.send_conversation()

    def update_current_line(self, text):
        """تحديث السطر الحالي مع الاحتفاظ بالجمل السابقة"""
        if self.conversation_history:
            display_text = "\n".join(self.conversation_history) + "\n" + text
        else:
            display_text = text
        
        # استخدام الإشارة بدلاً من التحديث المباشر
        self.update_display_request.emit(display_text)

    def update_display(self, text):
        """إرسال طلب تحديث العرض عبر الإشارة"""
        self.update_display_request.emit(text)

    def should_send(self, text):
        has_trigger = any(word in text for word in self.trigger_words)
        has_punctuation = any(text.endswith(p) for p in self.ending_punctuation)
        return has_trigger or has_punctuation

    def check_silence(self):
        if time.time() - self.last_activity_time > self.max_silence:
            if self.conversation_history:
                self.send_conversation()

    def send_conversation(self):
        full_text = "\n".join(self.conversation_history)
        self.button_send.click()
        self.conversation_history = []
        self.update_display("")
        self.play_sound('send')

    def stop_listening(self):
        self.is_listening = False
        self.listening_flag = False
        self.listening_state_changed.emit(False)
        self.update_button_style(False)
        self.play_sound('stop')
        self.silence_timer.stop()
        
        if self.conversation_history:
            self.send_conversation()

    def update_button_style(self, active):
        color = "#ffda03" if active else "lightblue"
        self.button_voice.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }}
        """)

    def play_sound(self, sound_type):
        try:
            import winsound
            freq = {'start': 1000, 'stop': 800, 'send': 1200}.get(sound_type, 500)
            winsound.Beep(freq, 200)
        except:
            pass
