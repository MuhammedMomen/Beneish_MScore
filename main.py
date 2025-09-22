# main.py - Entry point and main application controller
import flet as ft
from flet.flet_socket_server import PageCommandResponsePayload
from controllers.beneish_controller import BeneishController
from models.translation import TranslationManager
from utils.config import Config
import os
from dotenv import load_dotenv

def main(page: ft.Page):
    page.auto_scroll = True
    page.window.full_screen = True
    # Load environment variables
    load_dotenv()
    
    # Initialize config and translation
    config = Config()
    translation_manager = TranslationManager()
    
    # Initialize controller
    controller = BeneishController(page, config, translation_manager)
    
    # Setup page
    controller.setup_page()
    
    # Start the application
    controller.initialize_app()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")