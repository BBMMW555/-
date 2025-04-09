
# ------------------------ استيراد المكتبات ------------------------
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication,
   QLabel, QPushButton, QTextEdit, QLineEdit, 
   QFrame, QGraphicsDropShadowEffect, QMessageBox)
from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer, QRect
from PyQt5.QtGui import QColor, QPixmap, QTextCursor,QMovie

from voice_handler import VoiceHandler
from thinking_dialog import ThinkingDialog
from event_handlers import MessageHandler
from mouse_events import MouseEvents
from database import AILearningDatabase  # <-- أضف هذا الاستيراد
from context_manager import ContextManager

from response_handler import ResponseHandler
from smart_learning import SmartLearningDialog
from core import Core
from threading import Thread
import re

import random
import os


# ------------------------ تعريف نافذة التطبيق الرئيسية ------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.drag_pos = None
        self.is_dragging = False

        self.db = AILearningDatabase()  # <-- أضف هذا السطر
        self.context = ContextManager()  # <-- أضف هذا السطر
        
        # 1. تهيئة المتغيرات الأساسية فقط (بدون عناصر واجهة)
       
        self.message_handler = MessageHandler(self)
        self.thinking_dialog = None
        self.icon_pos = None
        
        self.dragging_from_icon = False
        self.mouse_offset = None
        self.response_handler = ResponseHandler(self.db, self.context)
        self.response_handler.response_ready.connect(self.handle_ai_response)
       
       
       
        QTimer.singleShot(100, self._setup_loading_indicator)
        self.core = Core(self) 

        # 2. تهيئة الواجهة أولاً
        self.initUI()

        # 3. تهيئة العناصر التي تعتمد على الواجهة
        self._setup_loading_indicator()
        
        self.voice_handler = VoiceHandler(
            chat_area=self.chat_area,
            entry=self.input_field,
            button_voice=self.button_voice,
            button_send=self.button_send
        )
        self.core.init_voice_handler()
        
        self.mouse_events = MouseEvents(self)
        self.bind_events()
        
        # 4. إظهار النافذة وإعداد الرسالة الترحيبية
        self.show()
        QTimer.singleShot(3000, self.welcome_message)

    # ------------------------ تهيئة واجهة المستخدم ------------------------
    def initUI(self):

        self.chat_area = QTextEdit()
        self.input_field = QTextEdit()
        self.button_voice = QPushButton()
        self.button_send = QPushButton()
        # خصائص النافذة
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 400, 600)  # زيادة الارتفاع قليلاً

        # إعداد التخطيط الأساسي
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # إنشاء أقسام الواجهة بالترتيب
        self.create_icon()
        self.create_chat_frame()
        self.create_input_area()
        self.create_control_buttons()

        # ربط الأحداث
        self.icon.installEventFilter(self)

        self.voice_handler = VoiceHandler(
            chat_area=self.chat_area,
            entry=self.input_field,
            button_voice=self.button_voice,
            button_send=self.button_send
        )

    # ------------------------ إنشاء الأيقونة ------------------------
    def create_icon(self):
        self.icon = QLabel()
        self.icon.setPixmap(QPixmap("C:/Users/bassam/Desktop/bassam/assets/icon.png").scaled(100, 100))
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 0);
                border-radius: 50px;
                padding: 10px;
            }
        """)
        self.main_layout.addWidget(self.icon)

    # ------------------------ إنشاء إطار المحادثة ------------------------
    def create_chat_frame(self):
        self.chat_frame = QFrame()
        self.chat_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 220);
                border: 1px solid #bdc3c7;
                border-radius: 15px;
            }
        """)



        
        

     
        
        # إضافة ظل للإطار
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        self.chat_frame.setGraphicsEffect(shadow)
        
        self.chat_layout = QVBoxLayout(self.chat_frame)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(10)
        
        # إنشاء سجل المحادثة
        self.chat_area = QTextEdit()
        self.chat_area.setMinimumHeight(400)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 200);
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.chat_layout.addWidget(self.chat_area)
        self.main_layout.addWidget(self.chat_frame)

    # ------------------------ إنشاء منطقة إدخال الرسائل ------------------------
    def create_input_area(self):
        #مربع الحدث 
        entry_frame = QFrame()
        entry_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid gray;
                border-radius: 10px;
            }
        """)
        input_layout = QHBoxLayout(entry_frame)
        input_layout.setSpacing(5)

        # زر الميكروفون
        self.button_voice = QPushButton("🎤")
        self.button_voice.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)

        # حقل إدخال النص
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("اكتب رسالتك هنا...")
        self.input_field.setMaximumHeight(120)  # أقصى ارتفاع
        self.input_field.setFixedHeight(40)
        self.input_field.setLineWrapMode(QTextEdit.WidgetWidth)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)

        # زر إرسال الملفات
        self.file_btn = QPushButton("📁")
        self.file_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)

        # زر الإرسال
        self.button_send = QPushButton("➤")
        self.button_send.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)

        # إضافة المكونات
        input_layout.addWidget(self.button_voice)
        input_layout.addWidget(self.input_field)# مربع نص ادخال
        input_layout.addWidget(self.file_btn)
        input_layout.addWidget(self.button_send)
        self.chat_layout.addWidget(entry_frame)

    # ------------------------ إنشاء أزرار التحكم ------------------------
    def create_control_buttons(self):
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid gray;
                border-radius: 10px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(50)

        # زر الإغلاق
        self.close_btn = QPushButton("إغلاق")
        self.close_btn.setFixedSize(50, 30)
        self.close_btn.setToolTip("إغلاق النافذة")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)
        

        # زر التطوير
        self.update_btn = QPushButton("🚀 تطوير")
        self.update_btn.setFixedSize(60, 30)
        self.update_btn.setToolTip("وضع التطوير")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)

        # زر الإعدادات
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setToolTip("الإعدادات")
        self.settings_btn.setFixedSize(40, 30)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)
        self.settings_btn.clicked.connect(self.show_smart_settings)

        # زر التفكير العميق
        self.think_btn = QPushButton("💭 تفكير عميق")
        self.think_btn.setToolTip("تفعيل وضع التفكير المتقدم")
        self.think_btn.setFixedSize(100, 30)
        self.think_btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffda03;
            }
        """)



        # إضافة الأزرار
        control_layout.addWidget(self.close_btn)
        control_layout.addWidget(self.update_btn)
        control_layout.addWidget(self.settings_btn)
        control_layout.addWidget(self.think_btn)
        self.chat_layout.addWidget(control_frame)

        
        # ------------------------ ربط الأحداث بالإشارات ------------------
    def bind_events(self):

        self.think_btn.clicked.connect(self.show_thinking_dialog)# تفعيل زر التفكير
        self.button_send.clicked.connect(self.send_message) # زر الارسال
        self.close_btn.clicked.connect(self.close) #تفعيل الغلاق
        self.button_voice.clicked.connect(self.toggle_microphone)

      
        self.mousePressEvent = self.mouse_events.on_press
        self.mouseMoveEvent = self.mouse_events.on_move
        self.mouseReleaseEvent = self.mouse_events.on_release


# ------------------------"وظيفة وسيطة للتعامل مع زر الميكروفون"---------------------

    def toggle_microphone(self):
    
        self.voice_handler.toggle_microphone()
        # يمكنك إضافة أي تحديثات للواجهة هنا إذا لزم الأمر

        # ------------------------ التعامل مع أحداث الماوس ---------------------
    def eventFilter(self, obj, event):
        """معالجة أحداث التمرير فوق الأيقونة"""
        if obj == self.icon:
            if event.type() == QEvent.Enter:
                if not self.chat_frame.isVisible():
                    self.chat_frame.show()
                    self.resize(400, 500)
                return True
            elif event.type() == QEvent.Leave:
                # إضافة هذا الجزء لتحسين التجربة
                pass
        return super().eventFilter(obj, event)

    
    #     # ------------------------ رسالة ترحيبية ------------------------
    def welcome_message(self):
        """عرض رسالة الترحيب للمستخدم عند تشغيل التطبيق"""
        welcome_text = (
            "مرحبًا! أنا ماني، مساعدك الذكي.\n"
            "كيف يمكنني مساعدتك اليوم؟"
        )
        self.update_chat_display(welcome_text, "النظام")

    def update_chat_display(self, message, sender):
        """تحديث عرض المحادثة"""
        if sender == "النظام":
            self.chat_area.append(f'<div style="color: #27ae60;"><b>{sender}:</b> {message}</div>')
        else:
            self.chat_area.append(f'<div style="color: #2980b9;"><b>{sender}:</b> {message}</div>')

    # ------------------------ وظيفة إرسال الرسالة ------------------------
    def send_message(self):
        message = self.input_field.toPlainText().strip()
        if message:
            self.display_message(message, "أنت")
            self.input_field.clear()
            self.show_loading_indicator()
            
            # تشغيل المعالجة في خيط منفصل
            Thread(target=self._process_message, args=(message,)).start()
    
    def _process_message(self, message):
        try:
            self.response_handler.process_message(message)
        except Exception as e:
            self.hide_loading_indicator()
            self.display_message("حدث خطأ أثناء المعالجة", "النظام")
         
   # ------------------------ "عرض الرسائل مع تنسيق متقدم بناءً على النمط والعاطفة"------------------------
    def display_message(self, text, sender, mode=None, emotion=None):
        # تنظيف النص قبل العرض
        text = self.clean_display_text(text)
        
        # تحديد الأنماط حسب الحالة
        styles = {
            "error": {"color": "#e74c3c", "bg": "#fadbd8"},
            "happy": {"color": "#27ae60", "bg": "#e8f5e9"},
            "sad": {"color": "#2980b9", "bg": "#e3f2fd"},
            "default": {"color": "#2c3e50", "bg": "#ffffff"}
        }
        
        style = styles.get(emotion, styles["default"])
        
        html = f'''
        <div style="margin:10px; text-align:{'left' if sender == 'أنت' else 'right'}">
            <div style="
                background:{style['bg']};
                color:{style['color']};
                border-radius:15px;
                padding:12px;
                display:inline-block;
                max-width:80%;
                border:1px solid {style['color']}55;
                animation:fadeIn 0.3s;
            ">
                <b>{sender}:</b> {text}
            </div>
        </div>
        '''
        
        self.chat_area.append(html)
        self.scroll_to_bottom()
    
    def clean_display_text(self, text):
        # إزالة المحتوى غير المرغوب
        text = re.sub(r'[.?؟!]{2,}', lambda m: m.group()[0], text)  # تقليل التكرارات
        text = re.sub(r'\s+', ' ', text)  # إزالة المسافات الزائدة
        return text.strip()[:400]  # تقييد الطول

    # ------------------------ مؤشر التحميل ------------------------
    def _setup_loading_indicator(self):
        """تهيئة مؤشر التحميل مع حل بديل"""
        self.loading_indicator = QLabel(self)
        self.loading_indicator.setAlignment(Qt.AlignCenter)
        
        # استخدام حل بديل بدون QMovie
        self._create_text_loading()
        
        self.loading_indicator.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 180);
                border-radius: 10px;
                padding: 15px;
                color: #555555;
                font-size: 14px;
                font-style: italic;
            }
        """)
        self.loading_indicator.hide()
        self.chat_layout.addWidget(self.loading_indicator)
    
    def _create_text_loading(self):
        """إنشاء مؤشر تحميل نصي بسيط"""
        self.loading_indicator.setText("... جاري تحضير الرد")
        
        # إنشاء مؤقت لتغيير النص
        self.loading_dots = 0
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self._update_loading_text)
        self.loading_timer.start(500)  # تحديث كل 500 مللي ثانية
    
    def _update_loading_text(self):
        """تحديث النص لمحاكاة الحركة"""
        dots = ["", ".", "..", "..."]
        self.loading_dots = (self.loading_dots + 1) % 4
        self.loading_indicator.setText(f"جاري تحضير الرد {dots[self.loading_dots]}")
        def show_loading_indicator(self):
            """عرض مؤشر التحميل مع التحكم في كلا النوعين"""
            if hasattr(self, 'loading_movie'):
                self.loading_movie.start()
            elif hasattr(self, 'loading_animation'):
                self.loading_animation.start()
                
            self.loading_indicator.show()
            self.chat_area.repaint()
        
    def show_loading_indicator(self):
        """عرض مؤشر التحميل"""
        if hasattr(self, 'loading_timer'):
            self.loading_timer.start()
        self.loading_indicator.show()
        self.chat_area.repaint()
    
    def hide_loading_indicator(self):
        """إخفاء مؤشر التحميل"""
        if hasattr(self, 'loading_timer'):
            self.loading_timer.stop()
        self.loading_indicator.hide()
    
    
    
    
    
    
    
    
                    
     #------------------------- """معالجة الردود القادمة من الذكاء الاصطناعي"""---------------  
    
    def handle_ai_response(self, text, mode, emotion):
        try:
            self.hide_loading_indicator()
            self.update_chat_style(mode)
            self.display_message(text, "ماني", mode, emotion)
            self.scroll_to_bottom()
            if self.thinking_dialog:
                self.thinking_dialog.close()
        except Exception as e:
            print(f"Error handling AI response: {str(e)}")
            self.display_message("حدث خطأ أثناء المعالجة", "النظام") 
    

     #-------------------------- """تحديث أنماط المحادثة بناءً على نوع الرد"""----------------   

    def update_chat_style(self, mode):
      
        styles = {
            "direct": {"bg": "#e8f5e9", "border": "#4CAF50"},
            "stable": {"bg": "#e3f2fd", "border": "#2196F3"},
            "creative": {"bg": "#fff3e0", "border": "#FF9800"},
            "happy": {"bg": "#fff8e1", "border": "#FFC107"},
            "emotional": {"bg": "#fce4ec", "border": "#E91E63"},
            "default": {"bg": "#ffffff", "border": "#cccccc"}
        }
        style = styles.get(mode, styles["default"])
        self.input_field.setStyleSheet(f"""
        QTextEdit {{
            background-color: {style['bg']};
            border: 2px solid {style['border']};
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }}
    """)
    
     #--------------------------- """التمرير إلى الأسفل بسلاسة""" -----------
    def scroll_to_bottom(self):
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    

    #----------------------------- فتح نافذة التفكير الذكي  -----------
    def show_thinking_dialog(self):
        """إصلاح خطأ text() واستبداله بـ toPlainText()"""
        user_input = self.input_field.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "تنبيه", "يرجى كتابة نص للتحليل.")
            return
        self.thinking_dialog = ThinkingDialog(self, user_input)
        self.thinking_dialog.show()

    #-----------------------------  """عرض نافذة الإعدادات الذكية""" -----------
    def show_smart_settings(self):
        """عرض نافذة الإعدادات الذكية"""
        settings_dialog = SmartLearningDialog(self)
        settings_dialog.exec_()    

    def show_error(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setText("حدث خطأ")
        error_box.setInformativeText(message)
        error_box.setWindowTitle("خطأ")
        error_box.exec_()
            


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())