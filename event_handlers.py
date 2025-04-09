# ------------------------ معالج الأحداث ------------------------
from ai_model import AraGPT2Assistant  # استيراد النموذج اللغوي
import re

class MessageHandler:
    def __init__(self, ui):
        """
        تهيئة معالج الأحداث.
        
        Args:
            ui (QWidget): الواجهة الرئيسية للتطبيق.
        """
        self.ui = ui
        self.ai = AraGPT2Assistant()  # تهيئة النموذج اللغوي
        
    def handle_message(self, message):
        """
        معالجة الرسالة المدخلة من المستخدم.
        
        Args:
            message (str): الرسالة المدخلة.
        """
        # تحديد نمط الرد (مستقر، إبداعي، افتراضي)
        mode = self.determine_mode(message)
        
        # تحديث واجهة المستخدم بناءً على النمط
        self.update_ui_style(mode)
        
        # توليد الرد باستخدام النموذج اللغوي
        response = self.generate_response(message, mode)
        
        # عرض الرد في واجهة المستخدم
        self.display_response(response)
        
    def determine_mode(self, message):
        """
        تحديد نمط الرد بناءً على الكلمات المفتاحية.
        
        Args:
            message (str): الرسالة المدخلة.
        
        Returns:
            str: النمط المحدد (مستقر، إبداعي، افتراضي).
        """
        message_lower = message.lower()
        
        # الكلمات المفتاحية للنمط المستقر
        stable_keywords = ["مستقر", "رد مباشر", "احتاج رد", "رد سريع"]
        
        # الكلمات المفتاحية للنمط الإبداعي
        creative_keywords = ["إبداعي", "خيالي", "مبتكر", "فكرة جديدة"]
        
        # التحقق من وجود الكلمات المفتاحية
        if any(kw in message_lower for kw in stable_keywords):
            return "مستقر"
        elif any(kw in message_lower for kw in creative_keywords):
            return "إبداعي"
        else:
            return "افتراضي"
        
    def generate_response(self, message, mode):
        """
        توليد الرد باستخدام النموذج اللغوي.
        
        Args:
            message (str): الرسالة المدخلة.
            mode (str): نمط الرد (مستقر، إبداعي، افتراضي).
        
        Returns:
            str: الرد المولد.
        """
        try:
            if mode == "مستقر":
                if "رد مباشر" in message.lower():
                    return "حسناً، ما هو الموضوع المحدد الذي تريد المناقشة فيه؟"
                else:
                    return self.ai.generate_response(
                        message,
                        max_new_tokens=100,
                        temperature=0.7,
                        do_sample=True
                    )
            elif mode == "إبداعي":
                return self.ai.generate_response(
                    message,
                    max_new_tokens=150,
                    temperature=0.9,
                    do_sample=True
                )
            else:
                return self.ai.generate_response(
                    message,
                    max_new_tokens=100,
                    temperature=0.8,
                    do_sample=True
                )
        except Exception as e:
            return f"حدث خطأ أثناء توليد الرد: {str(e)}"  # معالجة الأخطاء
        
    def update_ui_style(self, mode):
        """
        تحديث واجهة المستخدم بناءً على نمط الرد.
        
        Args:
            mode (str): نمط الرد (مستقر، إبداعي، افتراضي).
        """
        colors = {
            "مستقر": "#e8f5e9",  # أخضر فاتح
            "إبداعي": "#fff3e0",  # برتقالي فاتح
            "افتراضي": "white"
        }
        border_colors = {
            "مستقر": "#4CAF50",  # أخضر
            "إبداعي": "#FF9800",  # برتقالي
            "افتراضي": "#ccc"  # رمادي
        }
        
        # تحديث لون خلفية حقل الإدخال
        self.ui.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors.get(mode, 'white')};
                border: 2px solid {border_colors.get(mode, '#ccc')};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }}
        """)
        
    def display_response(self, response):
        """
        عرض الرد في واجهة المستخدم.
        
        Args:
            response (str): الرد المولد.
        """
        self.ui.chat_log.append(f'<div style="color: #27ae60;"><b>النظام:</b> {response}</div>')

  