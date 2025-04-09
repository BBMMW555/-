class SelfTester:
    def __init__(self, assistant):
        self.assistant = assistant
        
    def run_diagnostic(self):
        """فحص شامل للقدرات"""
        tests = [
            self._test_response_generation,
            self._test_system_integration,
            self._test_learning_capability
        ]
        
        results = {}
        for test in tests:
            results[test.__name__] = test()
        
        return results
    
    def _test_response_generation(self):
        """اختبار جودة الردود"""
        test_cases = [
            ("ما هو اسمك؟", "أنا ماني، مساعدك الذكي!"),
            ("كيف حالك؟", "أنا بخير، شكراً لسؤالك!")
        ]
        
        passed = True
        for input_text, expected in test_cases:
            response = self.assistant.generate_response(input_text)
            if expected not in response:
                passed = False
        return "ناجح" if passed else "فشل"