from database import AILearningDatabase
from response_handler import ResponseHandler
from voice_handler import VoiceHandler
from context_manager import ContextManager
import re



class Core:
    def __init__(self, main_window):  # <-- أضف main_window كمعامل
        self.main_window = main_window
        self.db = AILearningDatabase()
        self.context = ContextManager()
        self.response_handler = ResponseHandler(self.db, self.context)
        
        # تأجيل تهيئة voice_handler حتى بعد إنشاء واجهة المستخدم
        self.voice_handler = None

    def init_voice_handler(self):
        """تهيئة VoiceHandler بعد إنشاء عناصر واجهة المستخدم"""
        self.voice_handler = VoiceHandler(
            chat_area=self.main_window.chat_area,
            entry=self.main_window.input_field,
            button_voice=self.main_window.button_voice,
            button_send=self.main_window.button_send
        )
        # ربط الإشارات
        self.response_handler.response_ready.connect(self.voice_handler.update_display_slot)
    
    def setup_connections(self):
        self.response_handler.response_ready.connect(self.voice_handler.speak)
        self.voice_handler.text_recognized.connect(self.response_handler.process_message)