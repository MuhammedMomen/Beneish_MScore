# views/settings_view.py - Settings and configuration view
import flet as ft
from flet import Icons
from typing import Callable, Optional
from utils.config import Config
from models.translation import TranslationManager
from services.llm_service import LLMService

class SettingsView:
    def __init__(
        self,
        page: ft.Page,
        config: Config,
        translation_manager: TranslationManager,
        llm_service: LLMService,
        on_configured_callback: Callable
    ):
        self.page = page
        self.config = config
        self.translation_manager = translation_manager
        self.llm_service = llm_service
        self.on_configured_callback = on_configured_callback
        
        # --- UI Components ---
        # These are initialized in the build methods
        self.provider_dropdown: Optional[ft.Dropdown] = None
        self.model_dropdown: Optional[ft.Dropdown] = None
        self.api_key_input: Optional[ft.TextField] = None
        self.status_text: Optional[ft.Text] = None
        self.api_key_status_icon: Optional[ft.Icon] = None
        self.api_key_status_text: Optional[ft.Text] = None
        
    def build(self) -> ft.Control:
        """Build the settings view by assembling its sections."""
        return ft.Column(
            [
                self.build_provider_section(),
                ft.Container(height=10),
                self.build_api_key_section(),
                ft.Container(height=10),
                self.build_status_section()
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            width=500,
            height=600 # Adjusted for better layout
        )

    # --- Event Handlers ---

    def on_provider_changed(self, e: ft.ControlEvent):
        """Handle provider selection change"""
        provider = e.control.value
        
        # Update model options only after dropdown is created
        if self.model_dropdown is not None:
            self.update_model_options(provider)
            # Get the first available model for this provider
            if provider in self.config.llm_providers:
                models = self.config.llm_providers[provider].models
                if models:
                    # Configure the LLM service with provider and default model
                    api_key = self.config.get_api_key(provider)
                    if api_key:
                        self.llm_service.configure(provider, models[0], api_key)
        
        # Update API key status
        self._update_api_key_status(provider)
        
        # Update the page
        self.page.update()

    def on_api_key_changed(self, e: ft.ControlEvent):
        """Handle API key input change by clearing status messages."""
        self.status_text.value = ""
        self.status_text.color = self.config.colors.primary
        self.page.update()

    def test_configuration(self, e: ft.ControlEvent):
        """Test the current LLM configuration."""
        provider = self.provider_dropdown.value
        model = self.model_dropdown.value
        api_key = self.api_key_input.value
        
        if not provider or not model:
            self.status_text.value = "❌ Please select a provider and a model."
            self.status_text.color = self.config.colors.danger
            self.page.update()
            return
        
        if not self.config.is_provider_configured(provider) and not api_key:
            self.status_text.value = "❌ Please enter your API key."
            self.status_text.color = self.config.colors.danger
            self.page.update()
            return
        
        self.status_text.value = "🔄 Testing configuration, please wait..."
        self.status_text.color = self.config.colors.primary
        self.page.update()
        
        try:
            success = self.llm_service.initialize_llm(provider, model, api_key)
            if success:
                self.status_text.value = "✅ Configuration successful! Ready to use."
                self.status_text.color = self.config.colors.accent
                if self.on_configured_callback:
                    self.on_configured_callback()
            else:
                self.status_text.value = "❌ Configuration failed. Please check your API key and model selection."
                self.status_text.color = self.config.colors.danger
        except Exception as ex:
            self.status_text.value = f"❌ An error occurred: {str(ex)}"
            self.status_text.color = self.config.colors.danger
        
        self.page.update()
    
    # --- UI Update and Helper Methods ---
    
    def update_model_options(self, provider: str):
        """Update model options based on the selected provider."""
        if self.model_dropdown is None:
            return  # Dropdown not initialized yet
            
        if provider in self.config.llm_providers:
            models = self.config.llm_providers[provider].models
            self.model_dropdown.options = [ft.dropdown.Option(key=model, text=model) for model in models]
            if models:
                self.model_dropdown.value = models[0]
        else:
            self.model_dropdown.options = []
        self.model_dropdown.update()

    def _update_api_key_status(self, provider: Optional[str]):
        """Update the visual status of the API key requirement."""
        if not provider:
            self.api_key_status_icon.visible = False
            self.api_key_status_text.visible = False
            self.api_key_input.disabled = True
            return

        self.api_key_status_icon.visible = True
        self.api_key_status_text.visible = True

        has_key_in_env = self.config.is_provider_configured(provider)
        if has_key_in_env:
            self.api_key_status_icon.name = Icons.CHECK_CIRCLE_OUTLINED
            self.api_key_status_icon.color = self.config.colors.accent
            self.api_key_status_text.value = "API Key found in environment"
            self.api_key_status_text.color = self.config.colors.accent
            self.api_key_input.hint_text = "Using API key from environment"
            self.api_key_input.value = ""
            self.api_key_input.disabled = True
        else:
            provider_name = self.config.llm_providers[provider].display_name
            self.api_key_status_icon.name = Icons.WARNING_AMBER_ROUNDED
            self.api_key_status_icon.color = self.config.colors.warning
            self.api_key_status_text.value = "API Key required"
            self.api_key_status_text.color = self.config.colors.warning
            self.api_key_input.hint_text = f"Enter your {provider_name} API Key"
            self.api_key_input.disabled = False
    
    # --- UI Section Builders ---

    def build_provider_section(self) -> ft.Control:
        """Build the LLM provider and model selection section."""
        provider_options = [
            ft.dropdown.Option(key=pk, text=pv.display_name)
            for pk, pv in self.config.llm_providers.items()
        ]
        
        self.provider_dropdown = ft.Dropdown(
            label=self.translation_manager.get_text("select_provider"),
            options=provider_options,
            value=self.llm_service.current_provider,
            on_change=self.on_provider_changed,
        )
        
        self.model_dropdown = ft.Dropdown(
            label=self.translation_manager.get_text("model_selection"),
            disabled=not self.llm_service.current_provider
        )
        
        # Initialize model options if a provider is already selected
        if self.llm_service.current_provider:
            # Set options directly without calling update() since dropdown isn't on page yet
            provider = self.llm_service.current_provider
            if provider in self.config.llm_providers:
                models = self.config.llm_providers[provider].models
                self.model_dropdown.options = [ft.dropdown.Option(key=model, text=model) for model in models]
                if models and self.llm_service.current_model:
                    self.model_dropdown.value = self.llm_service.current_model
                elif models:
                    self.model_dropdown.value = models[0]
        
        return ft.Container(
            content=ft.Column([
                ft.Text("AI Provider Configuration", size=18, weight=ft.FontWeight.BOLD),
                self.provider_dropdown,
                self.model_dropdown
            ]),
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.PRIMARY),
            padding=15,
            border_radius=10
        )
    
    def build_api_key_section(self) -> ft.Control:
        """Build the API key configuration section."""
        self.api_key_input = ft.TextField(
            label="API Key", password=True, can_reveal_password=True,
            on_change=self.on_api_key_changed
        )
        
        self.api_key_status_icon = ft.Icon(size=20)
        self.api_key_status_text = ft.Text(size=14)
        
        test_button = ft.ElevatedButton(
            text="Test & Save Configuration",
            icon=Icons.PLAY_ARROW_ROUNDED,
            on_click=self.test_configuration,
            style=ft.ButtonStyle(bgcolor=self.config.colors.secondary, color=ft.colors.WHITE),
            width=300,
        )
        
        # Set the initial state of the API key section
        self._update_api_key_status(self.provider_dropdown.value)

        return ft.Container(
            content=ft.Column([
                ft.Row([self.api_key_status_icon, self.api_key_status_text]),
                ft.Container(height=5),
                self.api_key_input,
                ft.Container(height=10),
                test_button
            ]),
        )
    
    def build_status_section(self) -> ft.Control:
        """Build the section for showing current status and test results."""
        self.status_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)
        
        llm_config = self.llm_service.get_current_config()
        status_color = self.config.colors.accent if llm_config['status'] == 'Configured' else self.config.colors.warning
        
        config_info_controls = [
            ft.Text("Current Status", weight=ft.FontWeight.BOLD, size=16),
            ft.Text(f"Provider: {llm_config['provider'] or 'Not Set'}", size=14),
            ft.Text(f"Model: {llm_config['model'] or 'Not Set'}", size=14),
            ft.Text(f"Status: {llm_config['status']}", size=14, color=status_color)
        ]
        
        return ft.Container(
            content=ft.Column([
                *config_info_controls,
                ft.Divider(height=15, thickness=1),
                self.status_text
            ]),
            bgcolor=ft.colors.with_opacity(0.05, self.config.colors.accent),
            padding=15,
            border_radius=10,
        )