# models/translation.py - Translation and localization
from typing import Dict

class TranslationManager:
    def __init__(self, default_language: str = "en"):
        self.current_language = default_language
        self.translations = {
            "en": {
                # App Title and Navigation
                "app_title": "Beneish M-Score Financial Analysis Tool",
                "back": "Back",
                "help": "Help",
                "faq": "FAQ", 
                "about": "About",
                "settings": "Settings",
                "language": "Language",
                
                # File Upload
                "upload_title": "Upload Financial Statements",
                "upload_subtitle": "Supported formats: PDF, Excel (.xlsx, .xls), CSV",
                "upload_button": "Upload Financial Data",
                "processing": "Processing file...",
                "success": "Analysis completed successfully!",
                
                # API Configuration
                "api_key_required": "API Key Required",
                "api_key_subtitle": "Please configure your AI provider API key",
                "set_api_key": "Set API Key",
                "api_configured": "API Key configured successfully!",
                "invalid_api": "Invalid API Key. Please check and try again.",
                
                # LLM Provider
                "select_provider": "Select AI Provider",
                "provider_status": "Provider Status",
                "model_selection": "Select Model",
                
                # Analysis Steps
                "step_extracting": "Extracting text from file...",
                "step_analyzing": "Analyzing financial data...",
                "step_calculating": "Calculating Beneish ratios...",
                "step_complete": "Analysis complete!",
                
                # Results
                "results_title": "Beneish M-Score Analysis Results",
                "company_name": "Company Name",
                "extracted_data": "Extracted Financial Data",
                "year_1": "Year 1 (Previous)",
                "year_2": "Year 2 (Current)",
                "copy_data": "Copy Data",
                "ratios_title": "Financial Ratios Analysis",
                "m_score_title": "Beneish M-Score Result",
                "low_risk": "LOW RISK",
                "high_risk": "HIGH RISK",
                "low_risk_desc": "Company is not likely to have manipulated their earnings",
                "high_risk_desc": "Company is likely to have manipulated their earnings",
                "interpretation_guide": "Interpretation Guide:",
                "guide_low": "M-Score < -1.78: Low risk of earnings manipulation",
                "guide_high": "M-Score > -1.78: High risk of earnings manipulation",
                "rerun_analysis": "Run New Analysis",
                
                # Ratio Descriptions
                "dsri_desc": "Measures the change in accounts receivable relative to sales",
                "gmi_desc": "Compares gross margin between current and previous year", 
                "aqi_desc": "Measures the change in asset quality",
                "sgi_desc": "Measures the growth in sales from previous year",
                "depi_desc": "Measures the change in depreciation rate",
                "sgai_desc": "Measures the change in SG&A expenses relative to sales",
                "lvgi_desc": "Measures the change in leverage",
                "tata_desc": "Measures total accruals as percentage of total assets",
                
                # Formula and Calculation Labels
                "formula_calculation": "Formula & Calculation",
                "formula_label": "Formula:",
                "calculation_label": "Calculation:",
                
                # Error Messages
                "error_file_read": "Error reading file. Please check the file format.",
                "error_no_data": "Could not extract financial data from the file.",
                "error_missing_data": "Some required financial data is missing.",
                "error_calculation": "Error calculating M-Score ratios.",
                "missing_values": "Missing Values",
                "incomplete_analysis": "Analysis incomplete due to missing data",
                
                # Help Dialog
                "help_title": "What is Beneish M-Score?",
                "help_content": """The Beneish M-Score is a mathematical model that uses eight financial ratios to detect whether a company has manipulated its earnings. 

It's a red flag tool that helps:
• Investors identify potential accounting fraud
• Auditors focus on high-risk companies  
• Analysts assess earnings quality
• Regulators detect suspicious financial reporting

The model assigns probabilities based on financial statement data. A score above -1.78 suggests higher likelihood of earnings manipulation.

This tool is for educational and analysis purposes only.""",
                
                # FAQ
                "faq_title": "Frequently Asked Questions",
                "faq_who": "Who should use this tool?",
                "faq_who_answer": """• Financial analysts and investors
• Auditors and accounting professionals
• Academic researchers and students
• Regulatory compliance teams
• Anyone studying financial statement analysis""",
                "faq_accuracy": "How accurate is the Beneish M-Score?",
                "faq_accuracy_answer": "The model has shown approximately 76% accuracy in detecting earnings manipulation in academic studies. However, it should be used as one tool among many in financial analysis.",
                "faq_data": "What financial data is required?",
                "faq_data_answer": "Two consecutive years of: Revenue, COGS, SG&A expenses, Depreciation, Net Income, Accounts Receivable, Current Assets, PPE, Securities, Total Assets, Current Liabilities, Long-term Debt, and Cash Flow from Operations.",
                
                # About
                "about_title": "About the Developer",
                "about_content": "This application was developed as a professional financial analysis tool.",
                "contact_email": "Contact Email",
                "business_card": "Business Contact",
                
                # Hardcoded UI strings
                "ai_extract_analyze": "AI will extract and analyze financial data",
                "view_results": "View Beneish M-Score results and interpretation",
                "red_flag_tool": "This is a red flag tool for earnings manipulation detection",
                "upload_instructions": "Upload financial statements (2 consecutive years)",
                "how_to_use_this_tool": "How to use this tool",
                "api_key_found_env": "API Key found in environment",
                "using_api_env": "Using API key from environment",
                "ai_provider_configuration": "AI Provider Configuration",
                "api_key": "API Key",
                "test_save_configuration": "Test & Save Configuration",
                "current_status": "Current Status",
                "provider": "Provider",
                "model": "Model",
                "status": "Status",
                "not_set": "Not Set",
                "developer_email": "developer@example.com",
                "company_name": "Financial Analysis Solutions",
                "website": "www.example.com",
                "api_key_required_input": "API Key required",
                "enter_api_key": "Enter your {provider} API Key",
                "ai_provider_config": "AI Provider Configuration",
                "api_key_label": "API Key",
                "test_save_config": "Test & Save Configuration",
                "current_status": "Current Status",
                "copy_data_tooltip": "Copy Data",
                "expand_data_tooltip": "Click to expand financial data details",
                "metric_column": "Metric",
                "formula_calc_details": "Formula & Calculation Details",
                "close_button": "Close"
            },
            "ar": {
                # App Title and Navigation (Arabic translations)
                "app_title": "نتيجة نموذج بينيش إم",
                "back": "رجوع",
                "help": "مساعدة",
                "faq": "أسئلة شائعة",
                "about": "حول",
                "settings": "الإعدادات", 
                "language": "اللغة",
                
                # File Upload
                "upload_title": "رفع البيانات المالية",
                "upload_subtitle": "الصيغ المدعومة: PDF, Excel (.xlsx, .xls), CSV",
                "upload_button": "رفع البيانات المالية",
                "processing": "جاري معالجة الملف...",
                "success": "تم إكمال التحليل بنجاح!",
                
                # API Configuration
                "api_key_required": "مفتاح API مطلوب",
                "api_key_subtitle": "يرجى تكوين مفتاح API لمزود الذكاء الاصطناعي",
                "set_api_key": "تعيين مفتاح API",
                "api_configured": "تم تكوين مفتاح API بنجاح!",
                "invalid_api": "مفتاح API غير صالح. يرجى المراجعة والمحاولة مرة أخرى.",
                
                # LLM Provider
                "select_provider": "اختيار مزود الذكاء الاصطناعي",
                "provider_status": "حالة المزود",
                "model_selection": "اختيار النموذج",
                
                # Analysis Steps
                "step_extracting": "استخراج النص من الملف...",
                "step_analyzing": "تحليل البيانات المالية...",
                "step_calculating": "حساب نسب بينيش...",
                "step_complete": "اكتمل التحليل!",
                
                # Results
                "results_title": "نتائج تحليل نتيجة بينيش إم",
                "company_name": "اسم الشركة",
                "extracted_data": "البيانات المالية المستخرجة",
                "year_1": "السنة 1 (السابقة)",
                "year_2": "السنة 2 (الحالية)",
                "copy_data": "نسخ البيانات",
                "ratios_title": "تحليل النسب المالية",
                "m_score_title": "نتيجة بينيش إم",
                "low_risk": "مخاطر منخفضة",
                "high_risk": "مخاطر عالية", 
                "low_risk_desc": "الشركة غير محتملة لتلاعب في الأرباح",
                "high_risk_desc": "الشركة محتملة لتلاعب في الأرباح",
                "interpretation_guide": "دليل التفسير:",
                "guide_low": "النتيجة < -1.78: مخاطر منخفضة لتلاعب في الأرباح",
                "guide_high": "النتيجة > -1.78: مخاطر عالية لتلاعب في الأرباح",
                "rerun_analysis": "تشغيل تحليل جديد",
                
                # Error Messages
                "error_file_read": "خطأ في قراءة الملف. يرجى فحص صيغة الملف.",
                "error_no_data": "لم يتمكن من استخراج البيانات المالية من الملف.",
                "error_missing_data": "بعض البيانات المالية المطلوبة مفقودة.",
                "error_calculation": "خطأ في حساب نسب النتيجة إم.",
                "missing_values": "قيم مفقودة",
                "incomplete_analysis": "التحليل غير مكتمل بسبب البيانات المفقودة",
                
                # Help Dialog  
                "help_title": "ما هي نتيجة بينيش إم؟",
                "help_content": """نتيجة بينيش إم هي نموذج رياضي يستخدم ثمانية نسب مالية لاكتشاف ما إذا كانت الشركة قد لاعبت في أرباحها.

إنها أداة إنذار مبكر تساعد:
• المستثمرين على تحديد الاحتيال المحاسبي المحتمل
• المدققين على التركيز على الشركات عالية المخاطر
• المحللين على تقييم جودة الأرباح  
• الجهات التنظيمية على اكتشاف التقارير المالية المشبوهة

يعين النموذج احتماليات بناءً على بيانات البيان المالي. النتيجة أعلى من -1.78 تشير إلى احتمالية أعلى لتلاعب في الأرباح.

هذه الأداة للأغراض التعليمية والتحليلية فقط.""",

                # FAQ Section
                "faq_title": "أسئلة شائعة",
                "faq_who": "من يجب أن يستخدم هذه الأداة؟",
                "faq_who_answer": """• المحللون الماليون والمستثمرون
• المدققون والمهنيون المحاسبيون
• الباحثون الأكاديميون والطلاب
• فرق الامتثال التنظيمي
• أي شخص يدرس تحليل البيانات المالية""",
                "faq_accuracy": "ما مدى دقة نتيجة بينيش إم؟",
                "faq_accuracy_answer": "أظهر النموذج دقة تقارب 76% في اكتشاف تلاعب الأرباح في الدراسات الأكاديمية. ومع ذلك، يجب استخدامه كأداة واحدة من بين العديد في التحليل المالي.",
                "faq_data": "ما البيانات المالية المطلوبة؟",
                "faq_data_answer": "سنتان متتاليتان من: الإيرادات، تكلفة البضائع المباعة، مصاريف البيع والإدارة العامة، الاستهلاك، صافي الدخل، الذمم المدينة، الأصول المتداولة، الممتلكات والمعدات، الأوراق المالية، إجمالي الأصول، الخصوم المتداولة، الديون طويلة الأجل، والتدفق النقدي من العمليات.",
                
                # About
                "about_title": "حول المطور",
                "about_content": "تم تطوير هذا التطبيق كأداة تحليل مالي مهنية.",
                "contact_email": "البريد الإلكتروني للتواصل",
                "business_card": "جهة الاتصال التجارية",
                
                # Hardcoded UI strings
                "ai_extract_analyze": "سيقوم الذكاء الاصطناعي باستخراج وتحليل البيانات المالية",
                "view_results": "عرض نتائج نتيجة بينيش إم والتفسير",
                "red_flag_tool": "هذه أداة إنذار مبكر لاكتشاف تلاعب الأرباح",
                "upload_instructions": "رفع البيانات المالية (سنتان متتاليتان)",
                "api_key_found_env": "تم العثور على مفتاح API في البيئة",
                "using_api_env": "استخدام مفتاح API من البيئة",
                "ai_provider_configuration": "إعداد مزود الذكاء الاصطناعي",
                "api_key": "مفتاح API",
                "test_save_configuration": "اختبار وحفظ الإعداد",
                "current_status": "الحالة الحالية",
                "provider": "المزود",
                "model": "النموذج",
                "status": "الحالة",
                "not_set": "غير محدد",
                "developer_email": "developer@example.com",
                "company_name": "حلول التحليل المالي",
                "website": "www.example.com",
                "api_key_required_input": "مفتاح API مطلوب",
                "enter_api_key": "أدخل مفتاح API الخاص بـ {provider}",
                "ai_provider_config": "تكوين مزود الذكاء الاصطناعي",
                "api_key_label": "مفتاح API",
                "test_save_config": "اختبار وحفظ التكوين",
                "current_status": "الحالة الحالية",
                "copy_data_tooltip": "نسخ البيانات",
                "expand_data_tooltip": "انقر لتوسيع تفاصيل البيانات المالية",
                "metric_column": "المقياس",
                "formula_calc_details": "تفاصيل الصيغة والحساب",
                "how_to_use_this_tool": "كيف يمكن استخدام هذه الأداة",
                "close_button": "إغلاق"
                
            },

        }
    
    def get_text(self, key: str) -> str:
        """Get translated text for the current language"""
        return self.translations.get(self.current_language, {}).get(
            key, self.translations["en"].get(key, key)
        )
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.translations:
            self.current_language = language
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their display names"""
        return {
            "en": "English",
            "ar": "العربية"
        }