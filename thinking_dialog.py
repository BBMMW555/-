# ------------------------ استيراد المكتبات -------------------------
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton, QFrame, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor

# ------------------------ نافذة التفكير العميق -------------------------
class ThinkingDialog(QDialog):
    def __init__(self, parent=None, user_input=""):
        super().__init__(parent)
        self.setWindowTitle("وضع التفكير المتقدم")
        self.setGeometry(100, 100, 700, 500)
        self.user_input = user_input.strip()  # تنظيف النص المدخل

        # ------------------------ التخطيط الرئيسي -------------------------
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ------------------------ الخطوات الثابتة -------------------------
        self.create_steps_section()

        # ------------------------ النصوص التحليلية -------------------------
        self.create_dynamic_log_section()

        # ------------------------ مؤشر التقدم -------------------------
        self.create_progress_bar()

        # ------------------------ أزرار التحكم -------------------------
        self.create_control_buttons()

        # ------------------------ المؤقت للتحليل -------------------------
        self.current_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_thinking_process)
        self.timer.start(700)  # تحديث كل 0.7 ثانية

    # ------------------------ إنشاء قسم الخطوات الثابتة -------------------------
    def create_steps_section(self):
        """
        إنشاء قسم الخطوات الثابتة مع العنوان الملون.
        """
        steps_frame = QFrame()
        steps_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        steps_layout = QVBoxLayout(steps_frame)

        # إضافة العنوان الملون
        title = QLabel("الخطوات الثابتة")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2980b9; /* أزرق مميز */
            }
        """)
        steps_layout.addWidget(title)

        # الخطوات
        self.steps = [
            {"text": "تحليل مدخلات المستخدم", "color": "green"},
            {"text": "فرز البيانات", "color": "blue"},
            {"text": "استخراج المعلومات الرئيسية", "color": "orange"},
            {"text": "بناء الفرضيات", "color": "purple"},
            {"text": "استخراج النتيجة النهائية", "color": "red"}
        ]

        for step in self.steps:
            label = QLabel(f'<span style="color: {step["color"]}; font-weight: bold;">{step["text"]}</span>')
            steps_layout.addWidget(label)

        self.layout.addWidget(steps_frame)

    # ------------------------ إنشاء النصوص التحليلية -------------------------
    def create_dynamic_log_section(self):
        """
        إنشاء منطقة النصوص التحليلية.
        """
        self.dynamic_log = QTextEdit()
        self.dynamic_log.setReadOnly(True)
        self.dynamic_log.setStyleSheet("""
            QTextEdit {
                background-color: rgba(240, 240, 240, 0.9);
                border: 1px solid #ccc;
                font-family: Arial;
                font-size: 14px;
                padding: 8px;
            }
        """)
        self.layout.addWidget(self.dynamic_log)

    # ------------------------ إنشاء مؤشر التقدم -------------------------
    def create_progress_bar(self):
        """
        إنشاء شريط التقدم.
        """
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid gray;
                border-radius: 10px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: lightblue;
            }
        """)
        self.layout.addWidget(self.progress_bar)

    # ------------------------ إنشاء أزرار التحكم -------------------------
    def create_control_buttons(self):
        """
        إنشاء أزرار التحكم.
        """
        buttons_layout = QHBoxLayout()
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: lightgray;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ff0000;
                color: white;
            }
        """)
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_button)

        self.layout.addLayout(buttons_layout)

    # ------------------------ تحديث التفكير -------------------------
    def update_thinking_process(self):
        """
        تحديث النصوص ومراحل التفكير.
        """
        thoughts = [
            f"تحليل النص: {self.user_input}",
            "جارٍ اكتشاف الكلمات المفتاحية...",
            "تم التعرف على الأنماط الرئيسية...",
            "جاري استخراج الروابط بين العناصر...",
            "توليد الأفكار المبتكرة...",
            "توليد النتيجة النهائية..."
        ]

        if self.current_step < len(thoughts):
            self.dynamic_log.append(thoughts[self.current_step])
            self.dynamic_log.moveCursor(QTextCursor.End)
            self.current_step += 1
            self.progress_bar.setValue(int((self.current_step / len(thoughts)) * 100))
        else:
            self.timer.stop()
            self.dynamic_log.append("\n✅ التحليل اكتمل بنجاح!")
            self.progress_bar.setValue(100)

        # ------------------------ تحديث النافذة الرئيسية -------------------------
        if hasattr(self.parent(), 'update_main_result'):
            self.parent().update_main_result(f"التحليل النهائي للنص:\n{self.user_input}\n\n✅ تحليل متكامل!")
