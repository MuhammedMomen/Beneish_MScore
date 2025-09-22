# views/main_view.py - Main upload view
import flet as ft
from flet import Icons
from typing import Callable
from utils.config import Config
from models.translation import TranslationManager
from services.llm_service import LLMService

class MainView:
    def __init__(
        self,
        page: ft.Page,
        config: Config,
        translation_manager: TranslationManager,
        llm_service: LLMService,
        on_upload_callback: Callable,
        progress_callback: Callable
    ):
        self.page = page
        self.config = config
        self.translation_manager = translation_manager
        self.llm_service = llm_service
        self.on_upload_callback = on_upload_callback
        self.progress_callback = progress_callback
        
        # UI Components
        self.progress_ring = ft.ProgressRing(visible=False)
        self.status_text = ft.Text("", size=14, color=self.config.colors.primary)
        self.upload_button = None
        
    def build(self) -> ft.Control:
        """Build the main view"""
        # Create upload button
        self.upload_button = ft.ElevatedButton(
            text=self.translation_manager.get_text("upload_button"),
            icon=Icons.UPLOAD_FILE,
            on_click=lambda _: self.on_upload_callback(),
            disabled=not self.llm_service.is_configured(),
            style=ft.ButtonStyle(
                bgcolor=self.config.colors.secondary if self.llm_service.is_configured() else ft.colors.GREY_400,
                color=ft.colors.WHITE,
                padding=ft.padding.all(15),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
            ),
            height=50,
            width=250
        )
        
        # LLM Status indicator
        llm_status = self.build_llm_status()
        
        # Main content
        main_content = ft.Container(
            content=ft.Column([
                # Header section
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            Icons.ANALYTICS,
                            size=80,
                            color=self.config.colors.primary
                        ),
                        ft.Text(
                            self.translation_manager.get_text("upload_title"),
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=self.config.colors.primary,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            self.translation_manager.get_text("upload_subtitle"),
                            size=16,
                            color=ft.colors.GREY_600,
                            text_align=ft.TextAlign.CENTER
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    margin=ft.margin.only(bottom=40)
                ),
                
                # LLM Status
                llm_status,
                
                # Upload section
                ft.Container(
                    content=ft.Column([
                        self.upload_button,
                        ft.Container(height=20),
                        ft.Row([
                            self.progress_ring,
                            self.status_text
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.colors.WHITE,
                    padding=40,
                    border_radius=15,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.colors.with_opacity(0.1, ft.colors.BLACK)
                    )
                ),
                
                # Instructions
                self.build_instructions()
                
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            expand=True
        )
        
        return main_content
    
    def build_llm_status(self) -> ft.Control:
        """Build LLM status indicator"""
        config = self.llm_service.get_current_config()
        is_configured = self.llm_service.is_configured()
        
        status_color = self.config.colors.accent if is_configured else self.config.colors.warning
        status_icon = Icons.CHECK_CIRCLE if is_configured else Icons.WARNING
        
        status_text = (
            f"{config['provider'].title()} - {config['model']}" 
            if is_configured else 
            self.translation_manager.get_text("api_key_required")
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(status_icon, color=status_color, size=20),
                ft.Text(
                    f"{self.translation_manager.get_text('provider_status')}: {status_text}",
                    size=14,
                    color=status_color,
                    weight=ft.FontWeight.BOLD if not is_configured else ft.FontWeight.NORMAL
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.with_opacity(0.1, status_color),
            padding=15,
            border_radius=10,
            border=ft.border.all(1, status_color),
            margin=ft.margin.only(bottom=30)
        )
    
    def build_instructions(self) -> ft.Control:
        """Build instructions section"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📊 How to use this tool:",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=self.config.colors.primary
                ),
                ft.Container(height=10),
                ft.Column([
                    self.create_instruction_item("1️⃣", "Upload financial statements (2 consecutive years)"),
                    self.create_instruction_item("2️⃣", "AI will extract and analyze financial data"),
                    self.create_instruction_item("3️⃣", "View Beneish M-Score results and interpretation"),
                    self.create_instruction_item("⚠️", "This is a red flag tool for earnings manipulation detection")
                ])
            ]),
            margin=ft.margin.only(top=40),
            padding=30,
            bgcolor=ft.colors.with_opacity(0.05, self.config.colors.primary),
            border_radius=10,
            border=ft.border.all(1, ft.colors.with_opacity(0.2, self.config.colors.primary))
        )
    
    def create_instruction_item(self, icon: str, text: str) -> ft.Control:
        """Create an instruction item"""
        return ft.Container(
            content=ft.Row([
                ft.Text(icon, size=16),
                ft.Text(text, size=14, color=ft.colors.GREY_700)
            ]),
            margin=ft.margin.only(bottom=8)
        )
    
    def update_progress(self, message: str):
        """Update progress message"""
        if "Error" in message or "❌" in message:
            self.status_text.color = self.config.colors.danger
            self.progress_ring.visible = False
        elif "complete" in message.lower() or "✅" in message:
            self.status_text.color = self.config.colors.accent
            self.progress_ring.visible = False
        else:
            self.status_text.color = self.config.colors.primary
            self.progress_ring.visible = True
        
        self.status_text.value = message
        self.page.update()
    
    def refresh_ui(self):
        """Refresh the UI components"""
        # Update upload button state
        is_configured = self.llm_service.is_configured()
        self.upload_button.disabled = not is_configured
        self.upload_button.style.bgcolor = (
            self.config.colors.secondary if is_configured else ft.colors.GREY_400
        )
        
        # Clear status
        self.status_text.value = ""
        self.progress_ring.visible = False
        
        self.page.update()