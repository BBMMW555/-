import pyautogui
import os
import subprocess

class SystemController:
    @staticmethod
    def open_app(app_name):
        """فتح تطبيق معين"""
        try:
            subprocess.Popen(app_name)
            return f"تم فتح {app_name}"
        except Exception as e:
            return f"خطأ في فتح التطبيق: {str(e)}"
    
    @staticmethod
    def monitor_screen():
        """مراقبة نشاط الشاشة الأساسي"""
        # يمكن تطوير هذا الجزء حسب الحاجة
        pass