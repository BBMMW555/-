
from datetime import datetime


#---------------------------ب. تحسين فهم السياق (context_manager.py جديد):------------------
class ContextManager:
    def __init__(self):
        self.context = {
            "last_messages": [],
            "current_topic": None,
            "user_info": {}
        }
    
    def get_context(self):  # دالة جديدة
        """الحصول على نسخة من السياق الحالي"""
        return self.context.copy()

    def update_context(self, message, response):
        """تحديث سياق المحادثة"""
        self.context["last_messages"].append((message, response))
        if len(self.context["last_messages"]) > 5:
            self.context["last_messages"].pop(0)
        
        # تحليل الموضوع إن وجد
        self._analyze_topic(message)

    def _analyze_topic(self, message):
        """تحليل الموضوع من الرسالة"""
        topic_keywords = {
            "مشروع": "planning",
            "جدول": "scheduling",
            "تكاليف": "budget"
        }
        
        for kw, topic in topic_keywords.items():
            if kw in message:
                self.context["current_topic"] = topic
                break