from PyQt5.QtCore import QObject, pyqtSignal
import traceback
import random
from datetime import datetime
from typing import Optional, Tuple, Dict, List
import json
import re
from collections import defaultdict
from ai_model import AraGPT2Assistant



class ResponseHandler(QObject):
    response_ready = pyqtSignal(str, str, str)  # text, mode, emotion
    
    COMMON_RESPONSES = {
        r'اسمك|ما اسمك': ("أنا ماني، مساعدك الذكي!", "stable", "happy"),
        r'كيف حالك|أخبارك': ("أنا بخير دائمًا، شكرًا لسؤالك!", "stable", "happy"),
        r'مساعدة|مساعده': ("يمكنك طرح أي سؤال، سأحاول مساعدتك!", "creative", "neutral"),
        r'شكرًا|متشكر': ("العفو! دائمًا تحت الخدمة.", "direct", "happy")
    }

    def process_message(self, message):
        try:
            # التحقق من الاستجابات الشائعة أولاً
            msg_lower = message.lower()
            for pattern, response in self.COMMON_RESPONSES.items():
                if re.search(pattern, msg_lower):
                    return response
            
            # إذا لم يكن سؤالاً شائعاً
            return self.generate_ai_response(message)
            
        except Exception as e:
            return (f"Error: {str(e)}", "error", "neutral")

    def generate_ai_response(self, message):
        # توليد الرد من النموذج اللغوي
        raw_response = self.ai.generate_response(message)
        
        # تحديد العاطفة
        emotion = self.detect_emotion(raw_response)
        
        # تحديد نمط الرد
        mode = "creative" if any(kw in message for kw in ["رأيك", "تفسير"]) else "stable"
        
        return (raw_response, mode, emotion)

    def detect_emotion(self, text):
        positive_words = ["ممتاز", "شكرًا", "سعيد"]
        negative_words = ["مشكلة", "خطأ", "حزين"]
        
        if any(word in text for word in positive_words):
            return "happy"
        elif any(word in text for word in negative_words):
            return "sad"
        return "neutral"

    def __init__(self, db, context):
        super().__init__()
        self.db = db
        self.context = context
        self.learning_enabled = True
        self.conversation_history = []
        self.user_profile = {}
        self.ai = AraGPT2Assistant()
        self.current_mode = "stable"
        self.last_interaction = None
        self.max_response_length = 150
        
        self._setup_response_systems()
        self._load_initial_data()
        
        # إعدادات الأداء
        self.settings = {
            "max_processing_time": 3,
            "min_confidence": 0.6,
            "learning_rate": 0.1
        }

    def _setup_response_systems(self):
        """تهيئة أنظمة الاستجابة"""
        self.modes = {
            "direct": {
                "temperature": 0.5,
                "max_length": 80,
                "emoji": "⚡",
                "style": {"color": "#4CAF50", "bg": "#E8F5E9"}
            },
            "stable": {
                "temperature": 0.7,
                "max_length": 120,
                "emoji": "🔍",
                "style": {"color": "#2196F3", "bg": "#E3F2FD"}
            },
            "creative": {
                "temperature": 0.9,
                "max_length": 200,
                "emoji": "🎨",
                "style": {"color": "#FF9800", "bg": "#FFF3E0"}
            }
        }
        
        self.emotions = {
            "happy": {
                "responses": ["أهلاً بك! 😊", "يومك جميل! 🌞"],
                "triggers": ["مرحبا", "مساء الخير", "سعيد"]
            },
            "sad": {
                "responses": ["أنا هنا لمساعدتك 🫂", "يمكنك التحدث معي 💬"],
                "triggers": ["حزين", "تعبان", "مشكلة"]
            }
        }
        
        self.commands = {
            "وضع سريع": self._set_direct_mode,
            "وضع دقيق": self._set_stable_mode,
            "مساعدة": self._show_help
        }

    def _load_initial_data(self):
        """تحميل البيانات الأولية"""
        try:
            self.common_questions = self.db.get_common_questions() or {
                "ما هو اسمك؟": "أنا ماني، مساعدك الذكي!",
                "كيف حالك؟": "أنا بخير، شكراً لسؤالك!"
            }
        except Exception as e:
            print(f"خطأ في تحميل البيانات: {str(e)}")
            self.common_questions = {}
    
    def process_message(self, message: str):
        try:
            if not message.strip():
                return "الرجاء إدخال رسالة صحيحة", "error", "neutral"
                
            # التحقق من الأوامر
            lower_msg = message.lower()
            for cmd, handler in self.commands.items():
                if cmd in lower_msg:
                    return handler()
            
            # توليد الرد
            mode_settings = self.modes[self.current_mode]
            response = self.ai.generate_response(
                message,
                max_length=mode_settings["max_length"],
                temperature=mode_settings["temperature"]
            )
            
            # تحديد العاطفة بناء على المحتوى
            emotion = self._detect_emotion(message)
            return response, self.current_mode, emotion
            
        except Exception as e:
            error_msg = f"حدث خطأ: {str(e)}"
            return error_msg, "error", "neutral"
    
    def _detect_emotion(self, text):
        """تحليل العاطفة من النص"""
        if any(word in text for word in ["مرحبا", "اهلا", "سلام"]):
            return "happy"
        elif any(word in text for word in ["حزين", "مشكلة", "مساعدة"]):
            return "sad"
        return "neutral"

    def _enhance_response(self, response: str) -> str:
        """تحسين الرد النهائي"""
        # إزالة التكرار
        response = re.sub(r'\b(\w+)\b(?=.*\b\1\b)', '', response)
        # إضافة إيموجي
        emojis = ["✨", "🌟", "💡", "🎯"]
        return f"{response.strip()} {random.choice(emojis)}"

    def _set_direct_mode(self) -> Tuple[str, str]:
        self.current_mode = "direct"
        return "تم تفعيل الوضع السريع ⚡", "direct"

    def _set_stable_mode(self) -> Tuple[str, str]:
        self.current_mode = "stable"
        return "تم تفعيل الوضع الدقيق 🔍", "stable"

    def _show_help(self) -> Tuple[str, str]:
        help_text = """
        الأوامر المتاحة:
        - وضع سريع: ردود سريعة
        - وضع دقيق: ردود مفصلة
        - مساعدة: عرض هذه القائمة
        """
        return help_text, "stable"

    def _log_error(self, error: Exception, message: str):
        """تسجيل الأخطاء"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "error": str(error),
            "traceback": traceback.format_exc()
        }
        self.db.log_error(error_data)
        print(f"حدث خطأ: {error_data}")

    def save_conversation(self):
        """حفظ المحادثة في قاعدة البيانات"""
        if self.last_interaction:
            self.db.save_interaction({
                "input": self.last_interaction.get("user_message"),
                "output": self.last_interaction.get("ai_response"),
                "timestamp": datetime.now()
            })