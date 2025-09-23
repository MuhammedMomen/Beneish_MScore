# controllers/beneish_controller.py - Main application controller
import flet as ft
from flet import Icons
import asyncio
import threading
from typing import Optional
import pyperclip

from models.beneish_models import BeneishCalculator, AnalysisResult, AnalysisStage
from models.translation import TranslationManager
from services.llm_service import LLMService
from utils.config import Config
from views.main_view import MainView
from views.results_view import ResultsView
from views.settings_view import SettingsView

class BeneishController:
    def __init__(self, page: ft.Page, config: Config, translation_manager: TranslationManager):
        self.page = page
        self.config = config
        self.translation_manager = translation_manager
        self.llm_service = LLMService(config)
        self.calculator = BeneishCalculator()
        
        # Views
        self.main_view = None
        self.results_view = None
        self.settings_view = None
        
        # State
        self.current_view = "main"
        self.analysis_result: Optional[AnalysisResult] = None
        self.current_stage = AnalysisStage.IDLE
        
        # UI Components
        self.file_picker = None
        
    def setup_page(self):
        """Setup page configuration and theme"""
        self.page.title = self.translation_manager.get_text("app_title")
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 1400
        self.page.window_height = 900
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.rtl = self.translation_manager.get_current_language() == "ar"
        
        # Setup theme with Cairo fonts
        self.page.theme = ft.Theme(
            font_family="Cairo"
        )
        
        # Setup fonts
        self.page.fonts = {
            "Cairo": "fonts/Cairo-Regular.ttf",
            "Cairo-Light": "fonts/Cairo-Light.ttf",
            "Cairo-Medium": "fonts/Cairo-Medium.ttf"
        }
        
        # Setup AppBar
        self.setup_appbar()
        
        # Setup file picker
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.file_picker)
    
    def show_model_founder_dialog(self, e):
        """Show the model founder dialog"""
        if self.main_view:
            self.main_view.open_help_dialog(e)
    
    def setup_appbar(self):
        """Setup application bar with navigation and actions"""
        # Check if screen is small (mobile/tablet)
        is_small_screen = self.page.window.width < 800 if self.page.window.width else False
        
        if is_small_screen:
            # Use icon buttons for small screens
            actions = [
                ft.IconButton(
                    Icons.TRANSLATE,
                    tooltip=self.translation_manager.get_text("language"),
                    on_click=self.toggle_language,
                    icon_color=ft.colors.WHITE
                ),
                ft.IconButton(
                    Icons.PERSON,
                    tooltip=self.translation_manager.get_text("model_founder"),
                    on_click=self.show_model_founder_dialog,
                    icon_color=ft.colors.WHITE
                ),
                
                ft.IconButton(
                    Icons.HELP,
                    tooltip=self.translation_manager.get_text("help"),
                    on_click=self.show_help_dialog,
                    icon_color=ft.colors.WHITE
                ),
                ft.IconButton(
                    Icons.QUIZ,
                    tooltip=self.translation_manager.get_text("faq"),
                    on_click=self.show_faq_dialog,
                    icon_color=ft.colors.WHITE
                ),
                ft.IconButton(
                    Icons.INFO,
                    tooltip=self.translation_manager.get_text("about"),
                    on_click=self.show_about_dialog,
                    icon_color=ft.colors.WHITE
                ),
                ft.IconButton(
                    Icons.SETTINGS,
                    tooltip=self.translation_manager.get_text("settings"),
                    on_click=self.show_settings,
                    icon_color=ft.colors.WHITE
                )
            ]
        else:
            # Use text buttons for larger screens
            actions = [
                ft.TextButton(
                    text=self.translation_manager.get_text("model_founder"),
                    on_click=self.show_model_founder_dialog,
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                ),
                ft.TextButton(
                    text=self.translation_manager.get_text("language"),
                    on_click=self.toggle_language,
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                ),
                ft.TextButton(
                    text=self.translation_manager.get_text("help"),
                    on_click=self.show_help_dialog,
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                ),
                ft.TextButton(
                    text=self.translation_manager.get_text("faq"),
                    on_click=self.show_faq_dialog,
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                ),
                ft.TextButton(
                    text=self.translation_manager.get_text("about"),
                    on_click=self.show_about_dialog,
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                ),
                ft.TextButton(
                    text=self.translation_manager.get_text("settings"),
                    on_click=self.show_settings,
                    style=ft.ButtonStyle(color=ft.colors.WHITE)
                )
            ]
        
        # Add back button when not on main view
        leading = None
        if self.current_view != "main":
            leading = ft.IconButton(
                Icons.ARROW_BACK,
                tooltip=self.translation_manager.get_text("back"),
                on_click=self.go_to_main_view,
                icon_color=ft.colors.WHITE
            )
        
        self.page.appbar = ft.AppBar(
            leading=leading,
            title=ft.Text(
                self.translation_manager.get_text("app_title"),
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.WHITE
            ),
            center_title=False,
            bgcolor=self.config.colors.primary,
            actions=actions
        )
    
    def initialize_app(self):
        """Initialize the main application"""
        # Try to auto-configure LLM from environment
        self.auto_configure_llm()
        
        # Create and show main view
        self.show_main_view()
    
    def auto_configure_llm(self):
        """Try to auto-configure LLM from available API keys"""
        available_providers = self.config.get_available_providers()
        
        if available_providers:
            # Use the first available provider
            provider_name = list(available_providers.keys())[0]
            provider_config = available_providers[provider_name]
            default_model = provider_config.models[0]
            
            success = self.llm_service.initialize_llm(provider_name, default_model)
            if success:
                print(f"✅ Auto-configured {provider_config.display_name} with {default_model}")
    
    def show_main_view(self):
        """Show the main upload view"""
        self.current_view = "main"
        self.setup_appbar()
        
        self.main_view = MainView(
            self.page,
            self.config,
            self.translation_manager,
            self.llm_service,
            self.on_upload_clicked,
            self.update_progress
        )
        
        self.page.clean()
        self.page.add(self.main_view.build())
        self.page.update()
    
    def show_results_view(self, result: AnalysisResult):
        """Show the results view"""
        self.current_view = "results"
        self.analysis_result = result
        self.setup_appbar()
        
        self.results_view = ResultsView(
            self.page,
            self.config,
            self.translation_manager,
            result,
            self.on_copy_data,
            self.on_rerun_analysis
        )
        
        self.page.clean()
        self.page.add(self.results_view.build())
        self.page.update()
    
    def show_settings(self, e=None):
        """Show settings dialog or view"""
        self.settings_view = SettingsView(
            self.page,
            self.config,
            self.translation_manager,
            self.llm_service,
            self.on_llm_configured
        )
        
        # Show as dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.translation_manager.get_text("settings")),
            content=self.settings_view.build(),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda e: self.page.close(dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
    
    def close_dialog(self):
        """Close the current dialog - deprecated, use page.close() instead"""
        # This method is kept for backward compatibility but should not be used
        # Use page.close(dialog) instead
        pass
    
    def toggle_language(self, e):
        """Toggle between English and Arabic"""
        current_lang = self.translation_manager.get_current_language()
        new_lang = "ar" if current_lang == "en" else "en"
        self.translation_manager.set_language(new_lang)
        
        # Update page RTL
        self.page.rtl = new_lang == "ar"
        
        # Refresh current view
        if self.current_view == "main":
            self.show_main_view()
        elif self.current_view == "results" and self.analysis_result:
            self.show_results_view(self.analysis_result)
    
    def show_help_dialog(self, e):
        """Show help dialog"""
        help_content = ft.Column(
            rtl=True if self.translation_manager.current_language == 'ar' else False,
            controls=[
            ft.Text(
                self.translation_manager.get_text("help_content"),
                size=14
            )
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text(self.translation_manager.get_text("help_title")),
            content=help_content,
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda e: self.page.close(dialog)
                )
            ]
        )
        
        self.page.open(dialog)
    
    def show_faq_dialog(self, e):
        """Show FAQ dialog"""
        faq_content = ft.Column([
            ft.Text(
                self.translation_manager.get_text("faq_who"),
                weight=ft.FontWeight.BOLD,
                size=16
            ),
            ft.Text(
                self.translation_manager.get_text("faq_who_answer"),
                size=14
            ),
            ft.Container(height=10),
            ft.Text(
                self.translation_manager.get_text("faq_accuracy"),
                weight=ft.FontWeight.BOLD,
                size=16
            ),
            ft.Text(
                self.translation_manager.get_text("faq_accuracy_answer"),
                size=14
            ),
            ft.Container(height=10),
            ft.Text(
                self.translation_manager.get_text("faq_data"),
                weight=ft.FontWeight.BOLD,
                size=16
            ),
            ft.Text(
                self.translation_manager.get_text("faq_data_answer"),
                size=14
            )
        ], scroll=ft.ScrollMode.AUTO)
        
        dialog = ft.AlertDialog(
            title=ft.Text(self.translation_manager.get_text("faq_title")),
            content=ft.Container(
                rtl=True if self.translation_manager.current_language == 'ar' else False,
                content=faq_content,
                width=600,
                height=400
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda e: self.page.close(dialog)
                )
            ]
        )
        
        self.page.open(dialog)
    
    def show_about_dialog(self, e):
        """Show about dialog with developer contact"""
        about_content = ft.Column([
            ft.Text(
                self.translation_manager.get_text("about_content"),
                size=14
            ),
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(
                            self.translation_manager.get_text("business_card"),
                            weight=ft.FontWeight.BOLD,
                            size=16
                        ),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Icon(Icons.BUSINESS, size=20),
                            ft.Text(self.translation_manager.get_text("developer_title"), size=14, selectable=True)
                        ]),
                        ft.Row([
                            ft.Icon(Icons.EMAIL, size=20),
                            ft.TextButton(
                                content=ft.Text(
                                    self.translation_manager.get_text("developer_email"),
                                    size=14
                                ),
                                url=f"mailto:{self.translation_manager.get_text('developer_email')}",
                                style=ft.ButtonStyle(color=ft.colors.BLUE)
                            )
                        ]),
                        ft.Row([
                            ft.Icon(Icons.WEB, size=20),
                            ft.TextButton(
                                content=ft.Text(
                                    self.translation_manager.get_text("website"),
                                    size=14
                                ),
                                url=self.translation_manager.get_text("website"),
                                style=ft.ButtonStyle(color=ft.colors.BLUE)
                            )
                        ])
                    ]),
                    padding=15
                )
            )
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text(self.translation_manager.get_text("about_title")),
            content=ft.Container(
                rtl=True if self.translation_manager.current_language == 'ar' else False,
                content=about_content,
                width=400,
                height=250
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda e: self.page.close(dialog)
                )
            ]
        )
        
        self.page.open(dialog)
    
    def on_upload_clicked(self):
        """Handle upload button click"""
        if not self.llm_service.is_configured():
            self.show_settings()
            return
        
        self.file_picker.pick_files(
            allowed_extensions=self.config.supported_file_types
        )
    
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file selection"""
        if e.files:
            file = e.files[0]
            
            # Start analysis in background thread
            def run_analysis():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.analyze_file(file))
                    loop.close()
                except Exception as ex:
                    print(f"Analysis error: {ex}")
                    self.update_progress(f"Error: {str(ex)}")
            
            thread = threading.Thread(target=run_analysis)
            thread.daemon = True
            thread.start()
    
    async def analyze_file(self, file):
        """Analyze uploaded file"""
        try:
            self.current_stage = AnalysisStage.EXTRACTING
            self.update_progress(self.translation_manager.get_text("step_extracting"))
            
            # Extract text from file
            file_extension = file.name.split('.')[-1]
            file_content = self.llm_service.extract_text_from_file(file.path, file_extension)
            
            self.current_stage = AnalysisStage.ANALYZING
            self.update_progress(self.translation_manager.get_text("step_analyzing"))
            
            # Analyze with LLM
            financial_data = await self.llm_service.analyze_financial_data(
                file_content,
                progress_callback=self.update_progress
            )
            
            if not financial_data:
                raise ValueError(self.translation_manager.get_text("error_no_data"))
            
            self.current_stage = AnalysisStage.CALCULATING
            self.update_progress(self.translation_manager.get_text("step_calculating"))
            
            # Validate data and calculate ratios
            missing_fields = self.calculator.validate_data(
                financial_data.year_1_data,
                financial_data.year_2_data
            )
            
            ratios = None
            m_score = None
            risk_level = "UNKNOWN"
            interpretation = self.translation_manager.get_text("incomplete_analysis")
            
            if not missing_fields:
                ratios = self.calculator.calculate_ratios(
                    financial_data.year_1_data,
                    financial_data.year_2_data
                )
                m_score = self.calculator.calculate_m_score(ratios)
                risk_level, interpretation = self.calculator.interpret_score(m_score)
            
            # Create result
            result = AnalysisResult(
                company_name=financial_data.company_name,
                financial_data=financial_data,
                ratios=ratios,
                m_score=m_score,
                risk_level=risk_level,
                interpretation=interpretation,
                missing_fields=missing_fields,
                success=True
            )
            
            self.current_stage = AnalysisStage.COMPLETE
            self.update_progress(self.translation_manager.get_text("step_complete"))
            
            # Show results
            self.show_results_view(result)
            
        except Exception as e:
            self.current_stage = AnalysisStage.ERROR
            error_msg = self.get_human_readable_error(str(e))
            self.update_progress(f"❌ {error_msg}")
    
    def get_human_readable_error(self, error: str) -> str:
        """Convert technical errors to human-readable messages"""
        if "API key" in error.lower():
            return self.translation_manager.get_text("invalid_api")
        elif "file" in error.lower():
            return self.translation_manager.get_text("error_file_read")
        elif "extract" in error.lower():
            return self.translation_manager.get_text("error_no_data")
        else:
            return error
    
    def update_progress(self, message: str):
        """Update progress message in main view"""
        if self.main_view and hasattr(self.main_view, 'update_progress'):
            self.main_view.update_progress(message)
    
    def on_llm_configured(self):
        """Handle LLM configuration completion"""
        self.close_dialog()
        if self.main_view and hasattr(self.main_view, 'refresh_ui'):
            self.main_view.refresh_ui()
    
    def on_copy_data(self, data: str):
        """Handle copy data to clipboard"""
        try:
            pyperclip.copy(data)
            # Show success message
            self.show_snack_bar("Data copied to clipboard!")
        except Exception as e:
            self.show_snack_bar(f"Copy failed: {str(e)}")
    
    def show_snack_bar(self, message: str, color: str = None):
        """Show snack bar message"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        
        self.page.open(snack_bar)
    
    def on_rerun_analysis(self):
        """Handle rerun analysis request"""
        self.go_to_main_view()
    
    def go_to_main_view(self, e=None):
        """Navigate back to main view"""
        self.show_main_view()