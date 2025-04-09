from PyQt5.QtCore import QObject, pyqtSignal
from database import AILearningDatabase
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os

class LearningEngine(QObject):
    """
    محرك التعلم الذكي الذي يدير:
    - تحليل التفاعلات
    - تحسين النموذج
    - إدارة المعرفة
    - التكيف التلقائي
    """
    
    # إشارات PyQt
    learning_updated = pyqtSignal(dict)  # عند تحديث المعرفة
    model_improved = pyqtSignal(float)   # عند تحسين النموذج (نسبة التحسين)
    
    def __init__(self, model_name: str = "aubmindlab/aragpt2-base"):
        super().__init__()
        self.db = AILearningDatabase()
        self.setup_ai_model(model_name)
        self.setup_learning_parameters()
        
        # تحميل البيانات الأولية
        self.load_knowledge_base()
        self.load_common_patterns()
        
        # تهيئة مؤشرات الأداء
        self.performance_metrics = {
            'accuracy': 0.75,
            'response_time': 2.5,
            'adaptability': 0.65
        }
    
    def setup_ai_model(self, model_name: str):
        """تهيئة نموذج اللغة وال tokenizer"""
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            self.model_dir = "ai_model"
            
            # إنشاء مجلد النموذج إذا لم يكن موجوداً
            os.makedirs(self.model_dir, exist_ok=True)
            
            # تحميل الأوزان المحسنة إذا وجدت
            if os.path.exists(os.path.join(self.model_dir, "pytorch_model.bin")):
                self.model.load_state_dict(torch.load(os.path.join(self.model_dir, "pytorch_model.bin")))
            
            print("✅ تم تحميل النموذج بنجاح")
        except Exception as e:
            print(f"❌ خطأ في تحميل النموذج: {str(e)}")
            raise
    
    def setup_learning_parameters(self):
        """تهيئة معلمات التعلم"""
        self.learning_rates = {
            'fast': 0.001,    # للتعلم السريع من التصحيحات
            'normal': 0.0001, # للتعلم العام
            'slow': 0.00001   # للضبط الدقيق
        }
        
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.learning_rates['normal']
        )
        
        # أنماط التعلم المحددة مسبقاً
        self.patterns_config = {
            'technical': {
                'keywords': ['برمجة', 'كود', 'سكريبت', 'دالة', 'صنف'],
                'response_style': 'detailed'
            },
            'improvement': {
                'keywords': ['تحسين', 'تطوير', 'أفضل', 'أسرع'],
                'response_style': 'suggestive'
            },
            'error': {
                'keywords': ['خطأ', 'لا يعمل', 'مشكلة', 'إصلاح'],
                'response_style': 'diagnostic'
            }
        }
    
    def process_interaction(self, user_input: str, ai_response: str) -> Dict:
        """
        معالجة تفاعل جديد وتحديث أنظمة التعلم
        """
        # تحليل النص وتصنيفه
        analysis = self.analyze_interaction(user_input, ai_response)
        
        # تسجيل التفاعل في قاعدة البيانات
        self.db.log_conversation(
            user_input=user_input,
            ai_response=ai_response,
            category=analysis['detected_patterns'][0] if analysis['detected_patterns'] else None,
            rating=analysis.get('user_rating'),
            is_correct=analysis['is_correct']
        )
        
        # تحديث المعرفة إذا كان التفاعل مفيداً
        if analysis['is_valuable']:
            self.update_knowledge_base(user_input, ai_response, analysis)
        
        # تحسين النموذج إذا لزم الأمر
        if analysis['requires_improvement']:
            self.improve_model(analysis)
        
        return analysis
    
    def analyze_interaction(self, user_input: str, ai_response: str) -> Dict:
        """
        تحليل متقدم للتفاعل مع تحديد القيمة التعليمية
        """
        # الكشف عن الأنماط
        detected_patterns = self.detect_patterns(user_input)
        
        # تقييم جودة الرد (محاكاة - يمكن استبداله بتقييم حقيقي)
        is_correct = self.evaluate_response_quality(user_input, ai_response)
        
        # تحديد إذا كان التفاعل ذو قيمة تعليمية
        is_valuable = len(user_input.split()) > 5 and is_correct
        
        # تحديد إذا كان يحتاج لتحسين النموذج
        requires_improvement = not is_correct or any(
            p in detected_patterns for p in ['error', 'misunderstanding'])
        
        return {
            'detected_patterns': detected_patterns,
            'is_correct': is_correct,
            'is_valuable': is_valuable,
            'requires_improvement': requires_improvement,
            'user_rating': None  # يمكن الحصول عليه من واجهة المستخدم
        }
    
    def detect_patterns(self, text: str) -> List[str]:
        """
        الكشف عن أنماط التعلم في النص باستخدام تحليل متقدم
        """
        detected = []
        text_lower = text.lower()
        
        for pattern, config in self.patterns_config.items():
            if any(kw in text_lower for kw in config['keywords']):
                detected.append(pattern)
                self.db._update_pattern_count(pattern)
        
        # تحليل إضافي باستخدام نموذج اللغة
        if self.is_technical_question(text):
            if 'technical' not in detected:
                detected.append('technical')
        
        return detected
    
    def is_technical_question(self, text: str) -> bool:
        """
        تحديد إذا كان السؤال تقنياً باستخدام النموذج
        """
        inputs = self.tokenizer.encode_plus(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=64
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # تحليل النتائج (مثال مبسط)
        logits = outputs.logits[0, -1, :]
        tech_keywords = ['برمجة', 'كود', 'برنامج', 'سكريبت']
        tech_scores = [logits[self.tokenizer.convert_tokens_to_ids(kw)].item() for kw in tech_keywords]
        
        return np.mean(tech_scores) > 0.5
    
    def evaluate_response_quality(self, user_input: str, ai_response: str) -> bool:
        """
        تقييم جودة الرد باستخدام مقاييس متعددة
        """
        # 1. طول الرد
        if len(ai_response.split()) < 3:
            return False
        
        # 2. وجود كلمات غير مناسبة
        negative_phrases = ['لا أعرف', 'غير متأكد', 'عذراً', 'لا يمكنني']
        if any(phrase in ai_response for phrase in negative_phrases):
            return False
        
        # 3. تحليل تماسك الرد (مثال مبسط)
        input_keywords = set(user_input.lower().split())
        response_keywords = set(ai_response.lower().split())
        overlap = input_keywords.intersection(response_keywords)
        
        return len(overlap) >= 2
    
    def update_knowledge_base(self, user_input: str, ai_response: str, analysis: Dict):
        """
        تحديث قاعدة المعرفة بناءً على التفاعل الجديد
        """
        # استخراج الموضوع الرئيسي
        topic = self.extract_topic(user_input)
        
        # حساب درجة الثقة
        confidence = self.calculate_confidence(ai_response, analysis)
        
        # إضافة/تحديث المعرفة
        self.db.add_knowledge(
            topic=topic,
            details=ai_response,
            confidence=confidence
        )
        
        # إرسال إشارة بالتحديث
        self.learning_updated.emit({
            'topic': topic,
            'confidence': confidence,
            'patterns': analysis['detected_patterns']
        })
    
    def extract_topic(self, text: str) -> str:
        """
        استخراج الموضوع الرئيسي من النص
        """
        # استخدام علامات الاستفهام للأسئلة
        if '؟' in text or '?' in text:
            return text.split('؟')[0].split('?')[0].strip()
        
        # استخدام الكلمات المفتاحية
        keywords = ['عن', 'بخصوص', 'حول', 'يعني']
        for kw in keywords:
            if kw in text:
                return text.split(kw)[-1].strip()
        
        # إذا لم يتم العثور على موضوع واضح
        return ' '.join(text.split()[:5])
    
    def calculate_confidence(self, response: str, analysis: Dict) -> float:
        """
        حساب درجة الثقة في المعلومة
        """
        base_score = 0.7 if analysis['is_correct'] else 0.3
        
        # زيادة الدرجة بناءً على طول الرد
        length_factor = min(len(response.split()) / 50, 0.2)
        
        # زيادة الدرجة للأنماط التقنية
        pattern_factor = 0.1 if 'technical' in analysis['detected_patterns'] else 0
        
        return min(base_score + length_factor + pattern_factor, 1.0)
    
    def improve_model(self, analysis: Dict):
        """
        تحسين النموذج بناءً على التفاعلات الحديثة
        """
        try:
            # الحصول على التفاعلات الأخيرة للتعلم منها
            recent_interactions = self.get_recent_interactions(
                limit=10,
                pattern_filter=analysis['detected_patterns']
            )
            
            if not recent_interactions:
                return
            
            # تحضير بيانات التدريب
            inputs = [i['user_input'] for i in recent_interactions]
            input_ids = self.tokenizer(
                inputs,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=128
            ).input_ids
            
            # التدريب على الدفعة (batch)
            self.model.train()
            outputs = self.model(input_ids, labels=input_ids)
            loss = outputs.loss
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()
            
            # حفظ النموذج المحسن
            self.save_improved_model()
            
            # تحديث مقاييس الأداء
            self.update_performance_metrics(loss.item())
            
            # إرسال إشارة بنسبة التحسين
            improvement = 1 - (loss.item() / self.performance_metrics['accuracy'])
            self.model_improved.emit(improvement)
            
        except Exception as e:
            print(f"❌ خطأ في تحسين النموذج: {str(e)}")
    
    def get_recent_interactions(self, limit: int = 10, pattern_filter: List[str] = None) -> List[Dict]:
        """
        استرجاع التفاعلات الحديثة من قاعدة البيانات
        """
        cursor = self.db.conn.cursor()
        
        if pattern_filter:
            placeholders = ','.join(['?'] * len(pattern_filter))
            query = f"""
            SELECT user_input, ai_response 
            FROM conversations 
            WHERE category IN ({placeholders})
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            cursor.execute(query, (*pattern_filter, limit))
        else:
            cursor.execute("""
            SELECT user_input, ai_response 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT ?
            """, (limit,))
        
        return [{'user_input': row[0], 'ai_response': row[1]} for row in cursor.fetchall()]
    
    def save_improved_model(self):
        """حفظ النموذج المحسن"""
        torch.save(self.model.state_dict(), os.path.join(self.model_dir, "pytorch_model.bin"))
        self.tokenizer.save_pretrained(self.model_dir)
    
    def update_performance_metrics(self, recent_loss: float):
        """تحديث مقاييس الأداء"""
        # حساب دقة جديدة (معكوس للخسارة)
        new_accuracy = 1 - (recent_loss / 10)  # تطبيع الخسارة
        
        # تحديث المقاييس مع مراعاة التاريخ
        self.performance_metrics['accuracy'] = 0.9 * self.performance_metrics['accuracy'] + 0.1 * new_accuracy
        self.performance_metrics['response_time'] *= 0.95  # تحسن افتراضي بنسبة 5%
        self.performance_metrics['adaptability'] = min(self.performance_metrics['adaptability'] + 0.02, 1.0)
    
    def load_knowledge_base(self):
        """تحميل المعرفة الأساسية عند التشغيل"""
        # يمكن إضافة معرفة مسبقة هنا
        initial_knowledge = [
            ("البرمجة بلغة بايثون", "بايثون لغة برمجة عالية المستوى سهلة التعلم"),
            ("تحسين الأداء", "تحسين الأداء يتطلب تحليل الاختناقات وتطبيق الحلول المناسبة")
        ]
        
        for topic, details in initial_knowledge:
            self.db.add_knowledge(topic, details)
    
    def load_common_patterns(self):
        """تحميل الأنماط الشائعة عند التشغيل"""
        common_patterns = [
            ("برمجة", "كود, سكريبت, دالة, صنف"),
            ("تحسين", "تطوير, أفضل, أسرع, تحسين"),
            ("أخطاء", "خطأ, لا يعمل, مشكلة, إصلاح")
        ]
        
        cursor = self.db.conn.cursor()
        cursor.executemany("""
        INSERT OR IGNORE INTO learning_patterns (pattern_name, detection_keywords)
        VALUES (?, ?)
        """, common_patterns)
        self.db.conn.commit()
    
    def get_learning_stats(self) -> Dict:
        """الحصول على إحصائيات التعلم الحالية"""
        stats = self.db.get_learning_stats()
        
        # إضافة مقاييس الأداء
        stats['performance'] = self.performance_metrics
        
        # إضافة معلومات النموذج
        stats['model_info'] = {
            'name': 'AraGPT2',
            'version': '1.1',
            'last_improvement': datetime.now().strftime("%Y-%m-%d")
        }
        
        return stats
    
    

    
    def close(self):
        """إغلاق المحرك وحفظ الحالة"""
        self.db.close()
        self.save_improved_model()