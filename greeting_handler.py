from datetime import datetime
import random

#------------------------ج. تحسين معالجة التحيات (greeting_handler.py جديد):----------
class GreetingHandler:
    @staticmethod
    def get_greeting_response():
        """إرجاع تحية مناسبة حسب الوقت"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return random.choice([
                "صباح الخير! 🌞 كيف يمكنني مساعدتك اليوم؟",
                "أهلاً بك في هذا الصباح الجميل!"
            ])
        elif 12 <= hour < 18:
            return "مساء النور! 🌇 كيف حالك؟"
        else:
            return "مساء الخير! 🌙 كيف يمكنني مساعدتك؟"