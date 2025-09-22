import flet as ft
from flet import Icons
import pandas as pd
import json
import asyncio
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
import PyPDF2
import openpyxl
from io import StringIO
import threading

from dotenv import load_dotenv
load_dotenv()


# Pydantic model for structured output
class FinancialData(BaseModel):
    company_name: str = Field(description="Name of the company")
    year_1_data: Dict[str, float] = Field(description="Financial data for Year 1 (previous year)")
    year_2_data: Dict[str, float] = Field(description="Financial data for Year 2 (current year)")

@dataclass
class BeneishRatios:
    dsri: float  # Days Sales in Receivables Index
    gmi: float   # Gross Margin Index
    aqi: float   # Asset Quality Index
    sgi: float   # Sales Growth Index
    depi: float  # Depreciation Index
    sgai: float  # Selling, General & Admin Expenses Index
    lvgi: float  # Leverage Index
    tata: float  # Total Accruals to Total Assets

class BeneishCalculator:
    def __init__(self):
        self.llm = None
        self.setup_llm()
    
    def setup_llm(self):
        """Setup Google Gemini LLM"""
        # Try multiple ways to get the API key
        api_key = (
            os.getenv("GOOGLE_API_KEY") or 
            os.getenv("GEMINI_API_KEY") or 
            os.getenv("GOOGLE_GEMINI_API_KEY")
        )
        
        # Debug: Print if API key is found (without revealing the actual key)
        if api_key:
            print(f"API Key found: {api_key[:10]}..." if len(api_key) > 10 else "✅ API Key found")
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=api_key,
                    temperature=0.5
                )
                print("LLM initialized successfully")
            except Exception as e:
                print(f"Error initializing LLM: {e}")
                self.llm = None
        else:
            print("No API key found in environment variables")
            print("Please set one of: GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_GEMINI_API_KEY")
            
            # Option to set API key directly in code (for testing)
            # Uncomment and add your API key here if needed:
            # api_key = "YOUR_API_KEY_HERE"
            # if api_key and api_key != "YOUR_API_KEY_HERE":
            #     self.llm = ChatGoogleGenerativeAI(
            #         model="gemini-1.5-pro",
            #         google_api_key=api_key,
            #         temperature=0
            #     )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def extract_text_from_excel(self, file_path: str) -> str:
        """Extract text from Excel file"""
        df = pd.read_excel(file_path, sheet_name=None)
        text = ""
        for sheet_name, sheet_df in df.items():
            text += f"Sheet: {sheet_name}\n"
            text += sheet_df.to_string() + "\n\n"
        return text
    
    def extract_text_from_csv(self, file_path: str) -> str:
        """Extract text from CSV file"""
        df = pd.read_csv(file_path)
        return df.to_string()
    
    async def extract_financial_data(self, file_path: str, file_type: str) -> Optional[FinancialData]:
        """Extract financial data from file using LLM"""
        if not self.llm:
            raise ValueError("LLM not configured. Please set GOOGLE_API_KEY environment variable.")
        
        # Extract text based on file type
        if file_type.lower() == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_type.lower() in ['xlsx', 'xls']:
            text = self.extract_text_from_excel(file_path)
        elif file_type.lower() == 'csv':
            text = self.extract_text_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Setup parser and prompt
        parser = JsonOutputParser(pydantic_object=FinancialData)
        
        prompt = PromptTemplate(
            template="""
            You are a financial analyst expert. Extract the following financial data from the provided text for Beneish M-Score calculation.

            Extract data for TWO consecutive years (Year 1 = previous year, Year 2 = current year):

            Required fields for each year:
            - revenue (net sales/revenue)
            - cost_of_goods_sold 
            - selling_general_admin_expense
            - depreciation
            - net_income_continuing_operations
            - accounts_receivables
            - current_assets
            - property_plant_equipment
            - securities (long-term investments)
            - total_assets
            - current_liabilities
            - total_long_term_debt
            - cash_flow_operations

            Text to analyze:
            {text}

            {format_instructions}

            Return the extracted financial data in the specified JSON format. If some values are missing, use 0 as default.
            """,
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({"text": text})
            return FinancialData(**result)
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None
    
    def calculate_ratios(self, year_1: Dict[str, float], year_2: Dict[str, float]) -> BeneishRatios:
        """Calculate the 8 Beneish M-Score ratios"""
        
        # Days Sales in Receivables Index (DSRI)
        dsr_1 = (year_1['accounts_receivables'] / year_1['revenue']) * 365 if year_1['revenue'] != 0 else 0
        dsr_2 = (year_2['accounts_receivables'] / year_2['revenue']) * 365 if year_2['revenue'] != 0 else 0
        dsri = dsr_2 / dsr_1 if dsr_1 != 0 else 1
        
        # Gross Margin Index (GMI)
        gross_margin_1 = (year_1['revenue'] - year_1['cost_of_goods_sold']) / year_1['revenue'] if year_1['revenue'] != 0 else 0
        gross_margin_2 = (year_2['revenue'] - year_2['cost_of_goods_sold']) / year_2['revenue'] if year_2['revenue'] != 0 else 0
        gmi = gross_margin_1 / gross_margin_2 if gross_margin_2 != 0 else 1
        
        # Asset Quality Index (AQI)
        aqi_1 = 1 - ((year_1['current_assets'] + year_1['property_plant_equipment'] + year_1['securities']) / year_1['total_assets']) if year_1['total_assets'] != 0 else 0
        aqi_2 = 1 - ((year_2['current_assets'] + year_2['property_plant_equipment'] + year_2['securities']) / year_2['total_assets']) if year_2['total_assets'] != 0 else 0
        aqi = aqi_2 / aqi_1 if aqi_1 != 0 else 1
        
        # Sales Growth Index (SGI)
        sgi = year_2['revenue'] / year_1['revenue'] if year_1['revenue'] != 0 else 1
        
        # Depreciation Index (DEPI)
        depr_rate_1 = year_1['depreciation'] / (year_1['depreciation'] + year_1['property_plant_equipment']) if (year_1['depreciation'] + year_1['property_plant_equipment']) != 0 else 0
        depr_rate_2 = year_2['depreciation'] / (year_2['depreciation'] + year_2['property_plant_equipment']) if (year_2['depreciation'] + year_2['property_plant_equipment']) != 0 else 0
        depi = depr_rate_1 / depr_rate_2 if depr_rate_2 != 0 else 1
        
        # SGA Expenses Index (SGAI)
        sga_rate_1 = year_1['selling_general_admin_expense'] / year_1['revenue'] if year_1['revenue'] != 0 else 0
        sga_rate_2 = year_2['selling_general_admin_expense'] / year_2['revenue'] if year_2['revenue'] != 0 else 0
        sgai = sga_rate_2 / sga_rate_1 if sga_rate_1 != 0 else 1
        
        # Leverage Index (LVGI)
        leverage_1 = (year_1['current_liabilities'] + year_1['total_long_term_debt']) / year_1['total_assets'] if year_1['total_assets'] != 0 else 0
        leverage_2 = (year_2['current_liabilities'] + year_2['total_long_term_debt']) / year_2['total_assets'] if year_2['total_assets'] != 0 else 0
        lvgi = leverage_2 / leverage_1 if leverage_1 != 0 else 1
        
        # Total Accruals to Total Assets (TATA)
        income_before_extra = year_2['net_income_continuing_operations']
        tata = (income_before_extra - year_2['cash_flow_operations']) / year_2['total_assets'] if year_2['total_assets'] != 0 else 0
        
        return BeneishRatios(dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata)
    
    def calculate_m_score(self, ratios: BeneishRatios) -> float:
        """Calculate the Beneish M-Score"""
        m_score = (-4.840 + 0.920 * ratios.dsri + 0.528 * ratios.gmi + 0.404 * ratios.aqi + 
                  0.892 * ratios.sgi + 0.115 * ratios.depi - 0.172 * ratios.sgai + 
                  4.679 * ratios.tata - 0.327 * ratios.lvgi)
        return m_score
    
    def interpret_score(self, m_score: float) -> tuple[str, str]:
        """Interpret the M-Score result"""
        if m_score < -1.78:
            return "LOW RISK", "Company is not likely to have manipulated their earnings"
        else:
            return "HIGH RISK", "Company is likely to have manipulated their earnings"

class BeneishApp:
    def __init__(self):
        self.calculator = BeneishCalculator()
        self.financial_data = None
        self.file_picker = None
        self.page = None
        
        # Add API key input option in UI
        self.api_key_input = None
    
    def setup_api_key_manually(self, api_key: str):
        """Manually set up API key from UI"""
        try:
            self.calculator.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.5
            )
            return True
        except Exception as e:
            print(f"Error setting up API key: {e}")
            return False
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Beneish M-Score Calculator"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 1400
        page.window.height = 900
        page.scroll = ft.ScrollMode.AUTO
        page.appbar = self.header
        
        # Corporate color scheme
        primary_color = "#1e3a8a"
        secondary_color = "#3b82f6"
        accent_color = "#10b981"
        danger_color = "#ef4444"
        
        # Progress indicator
        progress_ring = ft.ProgressRing(visible=False)
        status_text = ft.Text("", size=14, color=primary_color)
        
        # Results containers
        ratios_container = ft.Container(visible=False)
        score_container = ft.Container(visible=False)
        
        # File picker
        def on_file_pick(e: ft.FilePickerResultEvent):
            if e.files:
                # Use threading to handle async operations properly
                def run_async_task():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(process_file(e.files[0]))
                        loop.close()
                    except Exception as ex:
                        print(f"Error in async task: {ex}")
                        status_text.value = f"Error: {str(ex)}"
                        progress_ring.visible = False
                        self.page.update()
                
                thread = threading.Thread(target=run_async_task)
                thread.daemon = True
                thread.start()
        
        self.file_picker = ft.FilePicker(on_result=on_file_pick)
        page.overlay.append(self.file_picker)
        
        # Header
        self.header = ft.AppBar(
            leading=ft.Row([
                ft.Icon(Icons.ANALYTICS, size=40, color="white"),
                ft.Text(
                    "Beneish M-Score Calculator",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Container(expand=True),
                ft.Text(
                    "Corporate Finance Institute",
                    size=14,
                    color="white",
                    opacity=0.8
                )
            ]),
            bgcolor=primary_color,
            padding=20,
            margin=ft.margin.only(bottom=20)
        )
        
        # API Key input section (if not configured)
        api_key_container = ft.Container(visible=not self.calculator.llm)
        if not self.calculator.llm:
            self.api_key_input = ft.TextField(
                label="Google Gemini API Key",
                password=True,
                hint_text="Enter your Google Gemini API key",
                width=400
            )
            
            def set_api_key(e):
                if self.api_key_input.value:
                    if self.setup_api_key_manually(self.api_key_input.value):
                        api_key_container.visible = False
                        status_text.value = "✅ API Key configured successfully!"
                        status_text.color = accent_color
                    else:
                        status_text.value = "❌ Invalid API Key. Please check and try again."
                        status_text.color = danger_color
                    self.page.update()
            
            api_key_button = ft.ElevatedButton(
                "Set API Key",
                on_click=set_api_key,
                style=ft.ButtonStyle(
                    bgcolor=accent_color,
                    color="white"
                )
            )
            
            api_key_container.content = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "⚠️ Google Gemini API Key Required",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=danger_color
                    ),
                    ft.Text(
                        "Please enter your Google Gemini API key to use the LLM features.",
                        size=14,
                        color="grey"
                    ),
                    ft.Container(height=10),
                    self.api_key_input,
                    ft.Container(height=10),
                    api_key_button,
                    ft.Container(height=10),
                    ft.Text(
                        "Get your API key from: https://aistudio.google.com/app/apikey",
                        size=12,
                        color="blue",
                        selectable=True,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#fff3cd",
                padding=20,
                border_radius=10,
                border=ft.border.all(1, "#ffeaa7"),
                margin=ft.margin.only(bottom=20)
            )
        upload_button = ft.ElevatedButton(
            "Upload Financial Data",
            icon=Icons.UPLOAD_FILE,
            on_click=lambda _: self.file_picker.pick_files(
                allowed_extensions=["pdf", "xlsx", "xls", "csv"]
            ) if self.calculator.llm else None,
            disabled=not self.calculator.llm,
            style=ft.ButtonStyle(
                bgcolor=secondary_color if self.calculator.llm else "grey",
                color="white",
                padding=15
            )
        )
        upload_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Upload Financial Statements",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=primary_color
                ),
                ft.Text(
                    "Supported formats: PDF, Excel (.xlsx, .xls), CSV",
                    size=14,
                    color="grey"
                ),
                ft.Container(height=20),
                ft.Row([
                    upload_button,
                    progress_ring,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                status_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="white",
            padding=30,
            border_radius=10,
            border=ft.border.all(1, "#e5e7eb"),
            margin=ft.margin.only(bottom=30)
        )
        
        async def process_file(file):
            progress_ring.visible = True
            status_text.value = "Processing file..."
            self.page.update()
            
            try:
                file_extension = file.name.split('.')[-1]
                self.financial_data = await self.calculator.extract_financial_data(
                    file.path, file_extension
                )
                
                if self.financial_data:
                    # Calculate ratios and M-Score
                    ratios = self.calculator.calculate_ratios(
                        self.financial_data.year_1_data,
                        self.financial_data.year_2_data
                    )
                    m_score = self.calculator.calculate_m_score(ratios)
                    risk_level, interpretation = self.calculator.interpret_score(m_score)
                    
                    # Update UI with results
                    update_results(ratios, m_score, risk_level, interpretation)
                    status_text.value = "Analysis completed successfully!"
                else:
                    status_text.value = "Failed to extract financial data from file"
                    
            except Exception as e:
                status_text.value = f"Error: {str(e)}"
                print(f"Processing error: {e}")
            
            progress_ring.visible = False
            self.page.update()
        
        def update_results(ratios: BeneishRatios, m_score: float, risk_level: str, interpretation: str):
            # Ratios explanation
            ratio_explanations = {
                "DSRI": "Measures the change in accounts receivable relative to sales",
                "GMI": "Compares gross margin between current and previous year",
                "AQI": "Measures the change in asset quality",
                "SGI": "Measures the growth in sales from previous year",
                "DEPI": "Measures the change in depreciation rate",
                "SGAI": "Measures the change in SG&A expenses relative to sales",
                "LVGI": "Measures the change in leverage",
                "TATA": "Measures total accruals as percentage of total assets"
            }
            
            # Create ratio cards
            ratio_cards = []
            ratio_values = [
                ("DSRI", ratios.dsri), ("GMI", ratios.gmi), ("AQI", ratios.aqi),
                ("SGI", ratios.sgi), ("DEPI", ratios.depi), ("SGAI", ratios.sgai),
                ("LVGI", ratios.lvgi), ("TATA", ratios.tata)
            ]
            
            for name, value in ratio_values:
                card = ft.Container(
                    content=ft.Column([
                        ft.Text(name, size=18, weight=ft.FontWeight.BOLD, color=primary_color),
                        ft.Text(f"{value:.3f}", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            ratio_explanations[name],
                            size=12,
                            color="grey",
                            text_align=ft.TextAlign.CENTER
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="white",
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(1, "#e5e7eb"),
                    width=300,
                    height=120
                )
                ratio_cards.append(card)
            
            ratios_container.content = ft.Column([
                ft.Text(
                    "Financial Ratios Analysis",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=primary_color
                ),
                ft.Container(height=10),
                ft.Row(
                    ratio_cards[:4],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    wrap=True
                ),
                ft.Container(height=10),
                ft.Row(
                    ratio_cards[4:],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    wrap=True
                )
            ])
            
            # M-Score result
            score_color = danger_color if m_score > -1.78 else accent_color
            
            score_container.content = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Beneish M-Score Result",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=primary_color,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                f"{m_score:.3f}",
                                size=48,
                                weight=ft.FontWeight.BOLD,
                                color=score_color,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                risk_level,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=score_color,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                interpretation,
                                size=16,
                                color="grey",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Interpretation Guide:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=primary_color
                            ),
                            ft.Text(
                                "• M-Score < -1.78: Low risk of earnings manipulation",
                                size=12,
                                color="grey"
                            ),
                            ft.Text(
                                "• M-Score > -1.78: High risk of earnings manipulation",
                                size=12,
                                color="grey"
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="white",
                        padding=30,
                        border_radius=15,
                        border=ft.border.all(2, score_color),
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.margin.only(top=30)
            )
            
            ratios_container.visible = True
            score_container.visible = True
            self.page.update()
        
        # Main layout
        page.add(
            ft.Container(
                content=ft.Column([
                    api_key_container,
                    upload_section,
                    ratios_container,
                    score_container
                ]),
                padding=20
            )
        )

def main():
    app = BeneishApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()