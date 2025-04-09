from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re

class AraGPT2Assistant:
    def __init__(self, model_name="aubmindlab/aragpt2-base"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
        self.stop_phrases = [
            "اتصلوا بنا", "صادم:", "الربح من الإنترنت", 
            "فيسبوك", "واتساب", "البريد الإلكتروني"
        ]

    def generate_response(self, prompt, max_length=150, temperature=0.7):
        try:
            # تنظيف المدخلات
            clean_prompt = self.clean_input(prompt)
            
            inputs = self.tokenizer.encode(
                clean_prompt, 
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)

            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.5,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            raw_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self.clean_output(raw_response, clean_prompt)
            
        except Exception as e:
            return f"Error: {str(e)}"

    def clean_input(self, text):
        # إزالة الروابط والأرقام
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\d+', '', text)
        return text.strip()[:500]  # تقييد طول المدخلات

    def clean_output(self, text, prompt):
        # إزالة النص المكرر
        text = text.replace(prompt, "").strip()
        
        # إزالة الجمل غير المرغوبة
        for phrase in self.stop_phrases:
            text = text.split(phrase)[0]
        
        # تقصير الجمل الطويلة
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if len(sentences) > 3:
            text = ". ".join(sentences[:3]) + "."
            
        # إزالة التكرارات
        text = re.sub(r'(\?|\.|!)\1+', r'\1', text)
        return text[:500]  # تقييد طول المخرجات