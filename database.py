import sqlite3
from datetime import datetime
import json
from typing import Optional, List, Dict, Any

class AILearningDatabase:
    def __init__(self, db_path="ai_learning.db"):
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.create_tables()
            print("تم الاتصال بقاعدة البيانات بنجاح")  # رسالة تأكيد
        except Exception as e:
            print(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
            raise
    
    def create_tables(self) -> None:
        """إنشاء جميع الجداول المطلوبة"""
        cursor = self.conn.cursor()
        
        # جدول المعلومات الشخصية (جديد)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS personal_info (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # جدول الأسئلة الشائعة (جديد)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS common_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE NOT NULL,
            answer TEXT NOT NULL,
            usage_count INTEGER DEFAULT 1,
            last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.execute("""
           CREATE TABLE IF NOT EXISTS conversations (
               id INTEGER PRIMARY KEY,
               user_input TEXT,
               ai_response TEXT,
               category TEXT,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
           )
       """)

        # ----- إضافة الفهارس هنا -----
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON conversations (category)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations (timestamp)")
        # ----------------------------

        self.conn.commit()

        
        # جدول التفاعلات الأساسية (معدل)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_valuable BOOLEAN DEFAULT 0,
            pattern_detected TEXT,
            sentiment TEXT,
            confidence REAL DEFAULT 0.5
        )
        """)
        
        # جدول أنماط التعلم (معدل)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_patterns (
            pattern_name TEXT PRIMARY KEY,
            detection_keywords TEXT NOT NULL,
            example_questions TEXT,
            count INTEGER DEFAULT 1,
            last_used DATETIME,
            response_style TEXT
        )
        """)
        
        # جدول التحسينات (معدل)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS improvements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER NOT NULL,
            improvement_type TEXT NOT NULL,
            details TEXT,
            improvement_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES interactions(id) ON DELETE CASCADE
        )
        """)
        
        # إنشاء فهارس لتحسين الأداء
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_count ON learning_patterns(count)")
        
        self.conn.commit()
    
    def get_common_questions(self) -> Dict[str, str]:
        """استرجاع الأسئلة الشائعة مع تحديث تاريخ الاستخدام"""
        try:
            cursor = self.conn.cursor()
            
            # استرجاع الأسئلة مرتبة حسب الأكثر استخداماً
            cursor.execute("""
            SELECT question, answer 
            FROM common_questions 
            ORDER BY usage_count DESC, last_used DESC
            """)
            
            results = cursor.fetchall()
            
            if not results:
                # إذا لم توجد أسئلة، نقوم بإضافة الأسئلة الافتراضية
                default_questions = [
                    ("ما هو اسمك؟", "أنا ماني، مساعدك الذكي!"),
                    ("كيف اتواصل معك", "يمكنك التحدث معي مباشرة هنا أو استخدام الأمر 'مساعدة'"),
                    ("من أنا", "أنت المستخدم الذي أتفاعل معه وأتعلم منه يومياً")
                ]
                
                cursor.executemany("""
                INSERT INTO common_questions (question, answer) 
                VALUES (?, ?)
                """, default_questions)
                
                self.conn.commit()
                return dict(default_questions)
            
            return dict(results)
            
        except sqlite3.Error as e:
            print(f"خطأ في استرجاع الأسئلة الشائعة: {str(e)}")
            return {}

    def update_question_usage(self, question: str) -> bool:
        """تحديث عداد استخدام السؤال"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE common_questions 
            SET 
                usage_count = usage_count + 1,
                last_used = CURRENT_TIMESTAMP
            WHERE question = ?
            """, (question,))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"خطأ في تحديث استخدام السؤال: {str(e)}")
            return False        


    def _initialize_default_data(self) -> None:
        """إدخال البيانات الأولية عند التشغيل الأول"""
        # ... (الكود الحالي)
        
        # تهيئة الأسئلة الشائعة إذا كان الجدول فارغاً
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM common_questions")
        if cursor.fetchone()[0] == 0:
            default_questions = [
                ("ما هو اسمك؟", "أنا ماني، مساعدك الذكي!"),
                ("كيف اتواصل معك", "يمكنك التحدث معي مباشرة هنا أو استخدام الأمر 'مساعدة'"),
                ("من أنا", "أنت المستخدم الذي أتفاعل معه وأتعلم منه يومياً")
            ]
            
            cursor.executemany("""
            INSERT INTO common_questions (question, answer) 
            VALUES (?, ?)
            """, default_questions)
            
        self.conn.commit()

    def find_similar_question(self, user_input: str) -> Optional[str]:
        """البحث عن سؤال مشابه في الأسئلة الشائعة"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT question 
            FROM common_questions 
            WHERE question LIKE ? 
            ORDER BY usage_count DESC 
            LIMIT 1
            """, (f"%{user_input}%",))
            
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"خطأ في البحث عن سؤال مشابه: {str(e)}")
            return None


    def save_personal_info(self, key: str, value: str) -> bool:
        """حفظ المعلومات الشخصية في قاعدة البيانات"""
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO personal_info (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving personal info: {str(e)}")
            return False

    def get_personal_info(self, key: str) -> Optional[str]:
        """استرجاع المعلومات الشخصية من قاعدة البيانات"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM personal_info WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error retrieving personal info: {str(e)}")
            return None

    def log_interaction(self, user_input: str, ai_response: str, 
                       is_valuable: bool = False, pattern: str = None,
                       sentiment: str = None, confidence: float = 0.5) -> Optional[int]:
        """تسجيل تفاعل جديد في قاعدة البيانات"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO interactions 
            (user_input, ai_response, is_valuable, pattern_detected, sentiment, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_input, ai_response, is_valuable, pattern, sentiment, confidence))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error logging interaction: {str(e)}")
            return None

    def detect_and_log_pattern(self, user_input: str) -> List[str]:
        """الكشف عن الأنماط وتحديثها في قاعدة البيانات"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT pattern_name, detection_keywords FROM learning_patterns")
            patterns = cursor.fetchall()
            
            detected = []
            for pattern_name, keywords_json in patterns:
                keywords = json.loads(keywords_json)
                if any(kw in user_input for kw in keywords):
                    detected.append(pattern_name)
                    self._update_pattern(pattern_name, user_input)
            
            return detected
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error detecting patterns: {str(e)}")
            return []

    def _update_pattern(self, pattern_name: str, example: str) -> bool:
        """تحديث بيانات النمط في قاعدة البيانات"""
        try:
            cursor = self.conn.cursor()
            
            # الحصول على الأمثلة الحالية
            cursor.execute("SELECT example_questions FROM learning_patterns WHERE pattern_name = ?", (pattern_name,))
            current_examples = cursor.fetchone()[0] or "[]"
            
            # تحديث الأمثلة
            examples = json.loads(current_examples)
            examples.append(example)
            if len(examples) > 5:  # حفظ آخر 5 أمثلة فقط
                examples = examples[-5:]
            
            # تحديث النمط
            cursor.execute("""
            UPDATE learning_patterns 
            SET count = count + 1,
                last_used = CURRENT_TIMESTAMP,
                example_questions = ?
            WHERE pattern_name = ?
            """, (json.dumps(examples, ensure_ascii=False), pattern_name))
            
            self.conn.commit()
            return True
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error updating pattern: {str(e)}")
            return False

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """استرجاع سجل المحادثات"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT user_input, ai_response, timestamp 
            FROM interactions 
            ORDER BY timestamp DESC 
            LIMIT ?
            """, (limit,))
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching conversation history: {str(e)}")
            return []

    def get_learning_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات التعلم"""
        stats = {
            "total_interactions": 0,
            "valuable_interactions": 0,
            "top_patterns": []
        }
        
        try:
            cursor = self.conn.cursor()
            
            # عدد التفاعلات الكلي
            cursor.execute("SELECT COUNT(*) FROM interactions")
            stats["total_interactions"] = cursor.fetchone()[0]
            
            # التفاعلات القيمة
            cursor.execute("SELECT COUNT(*) FROM interactions WHERE is_valuable = 1")
            stats["valuable_interactions"] = cursor.fetchone()[0]
            
            # الأنماط الأكثر استخداماً
            cursor.execute("""
            SELECT pattern_name, count 
            FROM learning_patterns 
            ORDER BY count DESC 
            LIMIT 3
            """)
            stats["top_patterns"] = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            print(f"Error getting learning stats: {str(e)}")
        
        return stats

    def close(self) -> None:
        """إغلاق اتصال قاعدة البيانات بشكل آمن"""
        try:
            if self.conn:
                self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database: {str(e)}")

    def __del__(self):
        """تنظيف الموارد عند الحذف"""
        self.close()

    def backup_database(self, backup_path: str) -> bool:
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            backup_conn = sqlite3.connect(backup_path)
            with backup_conn:
                self.conn.backup(backup_conn)
            backup_conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Backup failed: {str(e)}")
            return False
    
    # في ملف database.py
    def forget_knowledge(self, concept: str):
        """حذف مفهوم من قاعدة المعرفة"""
        query = "DELETE FROM knowledge_base WHERE concept = ?"
        self.cursor.execute(query, (concept,))
        self.conn.commit()