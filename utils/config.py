# utils/config.py - Configuration management
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class LLMConfig:
    name: str
    display_name: str
    models: List[str]
    api_key_env: str
    
@dataclass 
class AppColors:
    primary: str = "#1e3a8a"
    secondary: str = "#3b82f6"
    accent: str = "#10b981"
    danger: str = "#ef4444"
    warning: str = "#f59e0b"
    light_bg: str = "#f8fafc"
    card_bg: str = "#ffffff"

class Config:
    def __init__(self):
        self.colors = AppColors()
        self.supported_languages = ["en", "ar"]
        self.default_language = "en"
        
        # Latest LLM models based on research
        self.llm_providers = {
            "openai": LLMConfig(
                name="openai",
                display_name="OpenAI",
                models=[
                    "gpt-5",
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4.1-nano",
                    "o3",
                    "o4-mini"
                ],
                api_key_env="OPENAI_API_KEY"
            ),
            "anthropic": LLMConfig(
                name="anthropic", 
                display_name="Anthropic Claude",
                models=[
                    "claude-opus-4.1",
                    "claude-sonnet-4",
                    "claude-3.5-sonnet",
                    "claude-3.5-haiku"
                ],
                api_key_env="ANTHROPIC_API_KEY"
            ),
            "google": LLMConfig(
                name="google",
                display_name="Google Gemini", 
                models=[
                    "gemini-2.5-pro",
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                ],
                api_key_env="GOOGLE_API_KEY"
            )
        }
        
        self.supported_file_types = ["pdf", "xlsx", "xls", "csv"]
        self.max_file_size_mb = 50
        
    def get_api_key(self, provider: str) -> str:
        """Get API key for specified provider"""
        if provider not in self.llm_providers:
            return ""
        
        env_var = self.llm_providers[provider].api_key_env
        return os.getenv(env_var, "")
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if provider has valid API key"""
        return bool(self.get_api_key(provider))
    
    def get_available_providers(self) -> Dict[str, LLMConfig]:
        """Get all available providers with their config"""
        return {k: v for k, v in self.llm_providers.items() 
                if self.is_provider_configured(k)}