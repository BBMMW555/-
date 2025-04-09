from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, 
                            QFrame, QScrollArea, QTextEdit, QHBoxLayout,
                            QSizePolicy, QTableWidget, QTableWidgetItem,
                            QHeaderView, QLineEdit, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QTextCursor
import json
import os
from datetime import datetime

class SmartLearningDialog(QDialog):
    knowledge_updated = pyqtSignal(dict)  # إشارة عند تحديث المعرفة
    
    def __init__(self, parent=None, db_connection=None):
        super().__init__(parent)
        self.db = db_connection
        self.setWindowTitle("مركز التعلم الذكي - ماني")
        self.setMinimumSize(800, 900)  # حجم أكبر للواجهة
        self.learning_mode = False
        self.current_editing_id = None
        
        # تحميل البيانات الأولية
        self.knowledge_base = self.load_knowledge_base()
        self.programming_library = self.load_programming_library()
        
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        """تهيئة واجهة التعلم الذكي"""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        
        # شريط العنوان مع زر التعلم التفاعلي
        title_layout = QHBoxLayout()
        
        self.title = QLabel("مركز التعلم والتطوير - ماني")
        self.title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2ecc71);
            border-radius: 15px;
            color: white;
        """)
        self.title.setAlignment(Qt.AlignCenter)
        
        self.learning_btn = QPushButton("وضع التعلم التفاعلي")
        self.learning_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        self.learning_btn.setCheckable(True)
        self.learning_btn.clicked.connect(self.toggle_learning_mode)
        
        title_layout.addWidget(self.title)
        title_layout.addWidget(self.learning_btn)
        main_layout.addLayout(title_layout)
        
        # إطار معلومات التعلم
        info_frame = self.create_info_frame()
        main_layout.addWidget(info_frame)
        
        # إطار التحكم الرئيسي
        control_frame = self.create_control_frame()
        main_layout.addWidget(control_frame)
        
        # جدول المعرفة مع إمكانية التعديل
        self.knowledge_table = self.create_knowledge_table()
        main_layout.addWidget(self.knowledge_table)
        
        # منطقة التعديل التفاعلي
        edit_frame = self.create_edit_frame()
        main_layout.addWidget(edit_frame)
        
        # منطقة عرض التفاصيل
        self.detail_display = QTextEdit()
        self.detail_display.setReadOnly(False)
        self.detail_display.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        self.detail_display.setMinimumHeight(200)
        main_layout.addWidget(self.detail_display)
        
        # أزرار التنفيذ
        action_layout = QHBoxLayout()
        
        self.save_btn = self.create_action_button("💾 حفظ التعديلات", self.save_changes)
        self.cancel_btn = self.create_action_button("❌ إلغاء", self.cancel_editing)
        self.export_btn = self.create_action_button("📤 تصدير المعرفة", self.export_knowledge)
        self.import_btn = self.create_action_button("📥 استيراد المعرفة", self.import_knowledge)
        
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.cancel_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.import_btn)
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)

        guide_label = QLabel("💡 يمكنك قول 'مساعدة' أو النقر على الأزرار للاستكشاف")
        guide_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(guide_label)    
    
    def create_info_frame(self):
        """إنشاء إطار معلومات الأداء"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #ecf0f1;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #34495e;
            }
        """)
        
        layout = QHBoxLayout()
        
        # إحصائيات التعلم
        stats = self.db.get_learning_stats() if self.db else {
            'total_items': 0,
            'last_updated': 'غير متاح',
            'accuracy': '0%'
        }
        
        stats_labels = [
            f"المعرفة المخزنة: {stats['total_items']}",
            f"آخر تحديث: {stats['last_updated']}",
            f"دقة الإجابات: {stats['accuracy']}"
        ]
        
        for text in stats_labels:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        
        frame.setLayout(layout)
        return frame
    
    def create_control_frame(self):
        """إنشاء إطار أزرار التحكم"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # أزرار التحكم
        controls = [
        ("🧠 ما تعلمته", self.show_learned_knowledge),
        ("📊 تحليل التعلم", self.show_learning_analysis),
        ("📚 مكتبة البرمجة", self.show_programming_library),
        ("🔄 تحديث الذاتي", self.self_update),
        ("⚙️ إعدادات التعلم", self.show_learning_settings),
        ("💡 قدرات النظام", self.show_system_capabilities)  # زر جديد
    ]
    
        for text, handler in controls:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 8px;
                    margin: 0 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #2980b9;
                }
            """)
            btn.clicked.connect(handler)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(btn)
        
        frame.setLayout(layout)
        return frame
    
    def show_system_capabilities(self):
        """عرض إمكانيات النظام بشكل تفاعلي"""
        capabilities = [
            "التعرف على الصوت وتحويله إلى نص",
            "الرد على الأسئلة الشائعة",
            "التعلم التلقائي من التفاعلات",
            "إدارة سياق المحادثة",
            "التحديث الذاتي للنماذج"
        ]
        
        html_content = """
        <html>
            <body style='font-family: Arial;'>
                <h2 style='color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;'>
                    🚀 إمكانيات النظام
                </h2>
                <div style='background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 15px;'>
                    <ul style='list-style: none; padding-left: 0;'>
        """
        
        for cap in capabilities:
            html_content += f"""
            <li style='margin-bottom: 10px; padding: 10px; background: white; border-radius: 8px;'>
                <span style='color: #27ae60; font-size: 18px;'>•</span> {cap}
            </li>
            """
        
        html_content += """
                    </ul>
                    <p style='color: #7f8c8d; margin-top: 20px;'>
                        يمكنك تفعيل الميزات عبر الأزرار أو الأوامر الصوتية
                    </p>
                </div>
            </body>
        </html>
        """
        self.detail_display.setHtml(html_content)


    def create_knowledge_table(self):
        """إنشاء جدول المعرفة القابل للتعديل"""
        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 14px;
            }
            QHeaderView::section {
                background: #3498db;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "ID", "الفئة", "المفهوم", "التفاصيل", "آخر تعديل"
        ])
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.cellClicked.connect(self.show_knowledge_details)
        
        return table
    
    def create_edit_frame(self):
        """إنشاء إطار التعديل التفاعلي"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f1f8fe;
                border: 2px solid #bbdefb;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                font-weight: bold;
                color: #0d47a1;
            }
        """)
        
        layout = QVBoxLayout()
        
        # عنوان الإطار
        edit_title = QLabel("تعديل المعرفة:")
        edit_title.setAlignment(Qt.AlignRight)
        layout.addWidget(edit_title)
        
        # حقل التصنيف
        category_layout = QHBoxLayout()
        category_label = QLabel("التصنيف:")
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "برمجة", "رياضيات", "لغة", "عام", "شخصي"
        ])
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # حقل المفهوم
        concept_layout = QHBoxLayout()
        concept_label = QLabel("المفهوم:")
        self.concept_input = QLineEdit()
        self.concept_input.setPlaceholderText("أدخل المفهوم أو العنوان")
        
        concept_layout.addWidget(concept_label)
        concept_layout.addWidget(self.concept_input)
        layout.addLayout(concept_layout)
        
        # حقل التفاصيل
        details_label = QLabel("التفاصيل:")
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("أدخل التفاصيل الكاملة...")
        self.details_input.setMinimumHeight(100)
        
        layout.addWidget(details_label)
        layout.addWidget(self.details_input)
        
        frame.setLayout(layout)
        return frame
    
    def create_action_button(self, text, handler):
        """إنشاء زر تنفيذ مخصص"""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background: #219653;
            }
        """)
        btn.clicked.connect(handler)
        return btn
    
    def load_initial_data(self):
        """تحميل البيانات الأولية"""
        self.update_knowledge_table()
        
        # تحميل مكتبة البرمجة إذا لم تكن موجودة
        if not self.programming_library:
            self.load_default_programming_library()
    

    def update_knowledge_table(self):
        """تحديث جدول المعرفة"""
        self.knowledge_table.setRowCount(0)
        
        for item in self.knowledge_base:
            row_pos = self.knowledge_table.rowCount()
            self.knowledge_table.insertRow(row_pos)
            
            self.knowledge_table.setItem(row_pos, 0, QTableWidgetItem(str(item.get('id', ''))))
            self.knowledge_table.setItem(row_pos, 1, QTableWidgetItem(item.get('category', '')))
            self.knowledge_table.setItem(row_pos, 2, QTableWidgetItem(item.get('concept', '')))
            
            # عرض مختصر للتفاصيل
            details = item.get('details', '')
            short_details = (details[:50] + '...') if len(details) > 50 else details
            self.knowledge_table.setItem(row_pos, 3, QTableWidgetItem(short_details))
            
            self.knowledge_table.setItem(row_pos, 4, QTableWidgetItem(item.get('last_updated', '')))
      


    def show_knowledge_details(self, row, _):
        """عرض تفاصيل المعرفة عند النقر على صف"""
        self.current_editing_id = int(self.knowledge_table.item(row, 0).text())
        item = next((x for x in self.knowledge_base if x['id'] == self.current_editing_id), None)
        
        if item:
            # تعبئة حقول التعديل
            self.category_combo.setCurrentText(item['category'])
            self.concept_input.setText(item['concept'])
            
            # عرض التفاصيل مع تنسيق جميل
            details = item['details']
            html_content = f"""
            <html>
                <body style='font-family: Arial; font-size: 14px;'>
                    <h3 style='color: #2c3e50;'>{item['concept']}</h3>
                    <div style='color: #7f8c8d; margin-bottom: 10px;'>
                        <b>التصنيف:</b> {item['category']} | 
                        <b>آخر تعديل:</b> {item['last_updated']}
                    </div>
                    <div style='background: #f5f5f5; padding: 15px; border-radius: 8px;'>
                        {details.replace('\n', '<br>')}
                    </div>
                </body>
            </html>
            """
            self.detail_display.setHtml(html_content)
    
    def save_changes(self):
        """حفظ التعديلات على المعرفة"""
        if not self.current_editing_id:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد عنصر للتعديل")
            return
            
        # العثور على العنصر المطلوب
        item = next((x for x in self.knowledge_base if x['id'] == self.current_editing_id), None)
        if not item:
            QMessageBox.critical(self, "خطأ", "العنصر المحدد غير موجود")
            return
            
        # تحديث البيانات
        item.update({
            'category': self.category_combo.currentText(),
            'concept': self.concept_input.text(),
            'details':self.detail_display.toPlainText(),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        # حفظ في قاعدة البيانات
        if self.db:
            self.db.update_knowledge_item(item)
        
        # تحديث الواجهة
        self.update_knowledge_table()
        QMessageBox.information(self, "تم", "تم حفظ التعديلات بنجاح")
        
        # إرسال إشارة بالتحديث
        self.knowledge_updated.emit(item)
    
    def cancel_editing(self):
        """إلغاء عملية التعديل"""
        self.current_editing_id = None
        self.category_combo.setCurrentIndex(0)
        self.concept_input.clear()
        self.detail_document.clear()
        QMessageBox.information(self, "تم", "تم إلغاء التعديلات")
    
    def toggle_learning_mode(self, checked):
        """تبديل وضع التعلم التفاعلي"""
        self.learning_mode = checked
        
        if checked:
            self.learning_btn.setStyleSheet("""
                QPushButton {
                    background: #27ae60;
                    color: white;
                    font-weight: bold;
                }
            """)
            QMessageBox.information(
                self, 
                "وضع التعلم التفاعلي",
                "تم تفعيل وضع التعلم التفاعلي\n"
                "سأقوم الآن بطرح الأسئلة عندما أواجه معلومات غير واضحة"
            )
        else:
            self.learning_btn.setStyleSheet("""
                QPushButton {
                    background: #e74c3c;
                    color: white;
                    font-weight: bold;
                }
            """)

    def start_interactive_learning(self):
        """بدء جلسة تعلم تفاعلية مع المستخدم"""
        self.detail_display.setHtml("""
        <html>
            <body style='font-family: Arial;'>
                <h3 style='color: #2c3e50;'>مرحبا! أنا جاهز للتعلم 🎓</h3>
                <div style='background: #fff3cd; padding: 15px; border-radius: 8px;'>
                    <p>1. يمكنك تعليمي مفاهيم جديدة بالنقر على زر ➕</p>
                    <p>2. اسألني عن أي شيء لاستكشاف معرفتي</p>
                    <p>3. استخدم أمر 'صحح' لتحسين إجاباتي</p>
                </div>
            </body>
        </html>
        """)
        self._ask_first_question()
     
    def _ask_first_question(self):
        """طرح السؤال الأول"""
        self.ask_question("ما الموضوع الذي ترغب أن أتعلمه اليوم؟")
     
    def ask_question(self, question):
        """عرض سؤال للمستخدم"""
        self.detail_display.append(f"<b>ماني:</b> {question}")        
    
    def show_learned_knowledge(self):
        """عرض المعرفة المكتسبة"""
        categories = defaultdict(list)
        for item in self.knowledge_base:
            categories[item['category']].append(item['concept'])
        
        html_content = """
        <html>
            <body style='font-family: Arial;'>
                <h2 style='color: #2c3e50;'>المعرفة المكتسبة</h2>
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px;'>
        """
        
        for category, concepts in categories.items():
            html_content += f"""
            <h3 style='color: #3498db;'>{category}</h3>
            <ul style='margin-left: 20px;'>
            """
            
            for concept in concepts:
                html_content += f"<li>{concept}</li>"
            
            html_content += "</ul>"
        
        html_content += """
                </div>
                <p style='color: #27ae60; font-weight: bold;'>
                    إجمالي المفاهيم: {}
                </p>
            </body>
        </html>
        """.format(len(self.knowledge_base))
        
        self.detail_display.setHtml(html_content)
    
    def show_learning_analysis(self):
        """عرض تحليل التعلم"""
        stats = {
            'total_items': len(self.knowledge_base),
            'categories': defaultdict(int),
            'last_week_added': 0,
            'most_active_day': "غير معروف"
        }
        
        for item in self.knowledge_base:
            stats['categories'][item['category']] += 1
        
        html_content = """
        <html>
            <body style='font-family: Arial;'>
                <h2 style='color: #2c3e50;'>تحليل التعلم</h2>
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px;'>
                    <h3 style='color: #3498db;'>الإحصائيات الأساسية</h3>
                    <table border='1' style='border-collapse: collapse; width: 100%;'>
                        <tr>
                            <th style='padding: 8px; background: #3498db; color: white;'>المقياس</th>
                            <th style='padding: 8px; background: #3498db; color: white;'>القيمة</th>
                        </tr>
        """
        
        for name, value in stats.items():
            if name == 'categories':
                continue
                
            html_content += f"""
            <tr>
                <td style='padding: 8px;'>{name.replace('_', ' ')}</td>
                <td style='padding: 8px;'>{value}</td>
            </tr>
            """
        
        html_content += """
                    </table>
                    
                    <h3 style='color: #3498db; margin-top: 20px;'>التوزيع حسب التصنيف</h3>
                    <table border='1' style='border-collapse: collapse; width: 100%;'>
                        <tr>
                            <th style='padding: 8px; background: #3498db; color: white;'>التصنيف</th>
                            <th style='padding: 8px; background: #3498db; color: white;'>عدد المفاهيم</th>
                        </tr>
        """
        
        for category, count in stats['categories'].items():
            html_content += f"""
            <tr>
                <td style='padding: 8px;'>{category}</td>
                <td style='padding: 8px;'>{count}</td>
            </tr>
            """
        
        html_content += """
                    </table>
                </div>
            </body>
        </html>
        """
        
        self.detail_display.setHtml(html_content)
    
    def show_programming_library(self):
        """عرض مكتبة البرمجة"""
        html_content = """
        <html>
            <body style='font-family: Arial;'>
                <h2 style='color: #2c3e50;'>مكتبة أساسيات البرمجة</h2>
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px;'>
        """
        
        for category, items in self.programming_library.items():
            html_content += f"""
            <h3 style='color: #3498db;'>{category}</h3>
            <div style='margin-left: 20px;'>
            """
            
            for item in items:
                html_content += f"""
                <div style='background: white; padding: 10px; margin-bottom: 10px; border-radius: 5px; border-left: 4px solid #3498db;'>
                    <h4 style='color: #2c3e50; margin: 0;'>{item['title']}</h4>
                    <p style='margin: 5px 0; color: #7f8c8d;'>{item['description']}</p>
                    <pre style='background: #f5f5f5; padding: 10px; border-radius: 5px;'>{item['example']}</pre>
                </div>
                """
            
            html_content += "</div>"
        
        html_content += """
                </div>
                <p style='color: #27ae60; font-weight: bold;'>
                    يمكنك إضافة مفاهيم جديدة أو تعديل الموجودة عبر جدول المعرفة
                </p>
            </body>
        </html>
        """
        
        self.detail_display.setHtml(html_content)
    
    def self_update(self):
        """تحديث الذاتي للنظام"""
        reply = QMessageBox.question(
            self, 
            "تأكيد التحديث",
            "هل تريد حقاً تحديث نظام التعلم الذاتي؟\n"
            "هذه العملية قد تستغرق عدة دقائق.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # محاكاة عملية التحديث
            self.detail_document.clear()
            self.detail_document.setHtml("""
            <html>
                <body style='font-family: Arial;'>
                    <h3 style='color: #2c3e50;'>جاري التحديث الذاتي...</h3>
                    <div style='background: #fff3cd; padding: 15px; border-radius: 8px;'>
                        <p>🔍 تحليل المعرفة الحالية...</p>
                        <p>📊 تقييم الأداء...</p>
                        <p>🧠 تحسين النماذج...</p>
                        <p>💾 حفظ التغييرات...</p>
                    </div>
                    <p style='color: #27ae60; font-weight: bold;'>
                        تم التحديث بنجاح! النظام الآن أكثر ذكاءً.
                    </p>
                </body>
            </html>
            """)
            
            # في الواقع الفعلي، هنا سيتم استدعاء دوال التحديث
            if self.db:
                self.db.optimize_learning_models()
    
    def show_learning_settings(self):
        """عرض إعدادات التعلم"""
        settings_html = """
        <html>
            <body style='font-family: Arial;'>
                <h2 style='color: #2c3e50;'>إعدادات التعلم الذكي</h2>
                <div style='background: #f8f9fa; padding: 15px; border-radius: 10px;'>
                    <h3 style='color: #3498db;'>خيارات التعلم</h3>
                    <form>
                        <label>
                            <input type='checkbox' name='interactive_learning' checked>
                            التعلم التفاعلي (الطلب من المستخدم عند عدم الفهم)
                        </label><br>
                        
                        <label>
                            <input type='checkbox' name='auto_correction' checked>
                            التصحيح التلقائي عند اكتشاف الأخطاء
                        </label><br>
                        
                        <label>
                            <input type='checkbox' name='performance_logging' checked>
                            تسجيل أداء النظام
                        </label><br>
                        
                        <h3 style='color: #3498db; margin-top: 20px;'>مستوى التعلم</h3>
                        <select name='learning_level'>
                            <option value='basic'>أساسي</option>
                            <option value='intermediate' selected>متوسط</option>
                            <option value='advanced'>متقدم</option>
                        </select>
                    </form>
                </div>
            </body>
        </html>
        """
        
        self.detail_display.setHtml(settings_html)
    
    def export_knowledge(self):
        """تصدير قاعدة المعرفة"""
        # في الواقع الفعلي، سيتم حفظ الملف في مسار معين
        QMessageBox.information(
            self,
            "تم التصدير",
            "تم تصدير قاعدة المعرفة بنجاح.\n"
            "يمكنك العثور على الملف في مجلد التطبيق."
        )
    
    def import_knowledge(self):
        """استيراد قاعدة المعرفة"""
        reply = QMessageBox.question(
            self,
            "تأكيد الاستيراد",
            "هل تريد استيراد قاعدة معرفة جديدة؟\n"
            "هذا سيستبدل البيانات الحالية.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # محاكاة عملية الاستيراد
            self.detail_document.setHtml("""
            <html>
                <body style='font-family: Arial;'>
                    <h3 style='color: #2c3e50;'>جاري استيراد المعرفة...</h3>
                    <div style='background: #e8f4f8; padding: 15px; border-radius: 8px;'>
                        <p>📂 جاري تحميل الملف...</p>
                        <p>🔍 تحليل البيانات...</p>
                        <p>🧠 تحديث النماذج...</p>
                    </div>
                    <p style='color: #27ae60; font-weight: bold;'>
                        تم الاستيراد بنجاح! تمت إضافة {} عنصر جديد.
                    </p>
                </body>
            </html>
            """.format(len(self.knowledge_base)))
            
            # في الواقع الفعلي، سيتم قراءة الملف وتحديث البيانات
    
    def load_knowledge_base(self):
        """تحميل قاعدة المعرفة من قاعدة البيانات أو الملف"""
        if self.db:
            return self.db.get_all_knowledge()
        
        # نموذج افتراضي إذا لم تكن هناك قاعدة بيانات
        return [
            {
                "id": 1,
                "category": "برمجة",
                "concept": "حلقة for",
                "details": "تستخدم للتكرار عبر عناصر متسلسلة\nمثال:\nfor i in range(5):\n    print(i)",
                "last_updated": "2023-10-15"
            },
            {
                "id": 2,
                "category": "رياضيات",
                "concept": "نظرية فيثاغورس",
                "details": "في المثلث القائم، مربع الوتر يساوي مجموع مربعي الضلعين الآخرين",
                "last_updated": "2023-10-10"
            }
        ]
    
    def load_programming_library(self):
        """تحميل مكتبة البرمجة"""
        lib_path = os.path.join(os.path.dirname(__file__), "programming_library.json")
        
        if os.path.exists(lib_path):
            with open(lib_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # مكتبة افتراضية إذا لم يوجد ملف
        return {
            "Python": [
                {
                    "title": "الدوال Functions",
                    "description": "كائنات قابلة للاستدعاء تؤدي مهمة محددة",
                    "example": "def greet(name):\n    return f'Hello {name}!'"
                }
            ],
            "General Programming": [
                {
                    "title": "المتغيرات Variables",
                    "description": "حاويات لتخزين البيانات",
                    "example": "x = 5\ny = 'Hello'"
                }
            ]
        }
    
    def load_default_programming_library(self):
        """تحميل مكتبة البرمجة الافتراضية"""
        self.programming_library = {
            "أساسيات البرمجة": [
                {
                    "title": "المتغيرات",
                    "description": "حاويات لتخزين القيم",
                    "example": "س = ١٠\nاسم = \"أحمد\""
                },
                {
                    "title": "الشروط",
                    "description": "اتخاذ القرارات بناءً على شروط",
                    "example": "إذا (س > ٥) {\n    اطبع(\"كبير\")\n} وإلا {\n    اطبع(\"صغير\")\n}"
                }
            ],
            "البرمجة بلغة Python": [
                {
                    "title": "الدوال",
                    "description": "كتل من التعليمات البرمجية قابلة لإعادة الاستخدام",
                    "example": "def ضعف(س):\n    return س * ٢"
                }
            ]
        }
        
        # حفظ المكتبة الافتراضية
        lib_path = os.path.join(os.path.dirname(__file__), "programming_library.json")
        with open(lib_path, 'w', encoding='utf-8') as f:
            json.dump(self.programming_library, f, ensure_ascii=False, indent=4)
    
    def start_interactive_learning(self, question):
        """بدء جلسة تعلم تفاعلي"""
        if not self.learning_mode:
            return None
            
        # عرض سؤال للمستخدم
        reply = QMessageBox.question(
            self,
            "طلب مساعدة في التعلم",
            f"لم أفهم السؤال التالي بشكل كامل:\n\n{question}\n\nهل تريد مساعدتي في فهمه؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # فتح حوار تفاعلي للإدخال
            explanation, ok = QInputDialog.getText(
                self,
                "شرح المفهوم",
                "الرجاء شرح المفهوم أو الإجابة بشكل واضح:",
                QLineEdit.Normal,
                ""
            )
            
            if ok and explanation:
                # معالجة الشرح وإضافته للمعرفة
                new_knowledge = {
                    "category": "مستجد",
                    "concept": question[:50],  # استخدام جزء من السؤال كعنوان
                    "details": explanation,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }
                
                self.knowledge_base.append(new_knowledge)
                if self.db:
                    self.db.add_knowledge_item(new_knowledge)
                
                return explanation
        
        return None