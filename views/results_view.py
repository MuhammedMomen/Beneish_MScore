# views/results_view.py - Results display view
import flet as ft
from flet import Icons
from typing import Callable
from utils.config import Config
from models.translation import TranslationManager
from models.beneish_models import AnalysisResult, BeneishCalculator

class ResultsView:
    def __init__(
        self,
        page: ft.Page,
        config: Config,
        translation_manager: TranslationManager,
        result: AnalysisResult,
        copy_callback: Callable,
        rerun_callback: Callable
    ):
        self.page = page
        self.config = config
        self.translation_manager = translation_manager
        self.result = result
        self.copy_callback = copy_callback
        self.rerun_callback = rerun_callback
        
    def build(self) -> ft.Control:
        """Build the results view"""
        content = ft.Column([
            # Header with company name and action buttons
            self.build_header(),
            
            # Main results container
            ft.Container(
                content=ft.Column([
                    # M-Score result (prominent display)
                    self.build_m_score_card(),
                    
                    ft.Container(height=20),
                    
                    # Financial ratios
                    self.build_ratios_section(),
                    
                    ft.Container(height=20),
                    
                    # Extracted financial data (expandable)
                    self.build_data_section()
                ]),
                expand=True
            )
        ])
        
        return ft.Container(
            content=content,
            padding=20,
            expand=True
        )
    
    def build_header(self) -> ft.Control:
        """Build the header section"""
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        self.translation_manager.get_text("results_title"),
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.config.colors.primary
                    ),
                    ft.Text(
                        f"{self.translation_manager.get_text('company_name')}: {self.result.company_name}",
                        size=18,
                        color=self.config.colors.secondary
                    )
                ], expand=True),
                
                ft.ElevatedButton(
                    text=self.translation_manager.get_text("rerun_analysis"),
                    icon=Icons.REFRESH,
                    on_click=lambda _: self.rerun_callback(),
                    style=ft.ButtonStyle(
                        bgcolor=self.config.colors.secondary,
                        color=ft.colors.WHITE
                    )
                )
            ]),
            margin=ft.margin.only(bottom=30)
        )
    
    def build_m_score_card(self) -> ft.Control:
        """Build the M-Score result card"""
        if not self.result.m_score:
            # Show error state
            return ft.Container(
                content=ft.Column([
                    ft.Icon(Icons.WARNING, size=60, color=self.config.colors.warning),
                    ft.Text(
                        self.translation_manager.get_text("incomplete_analysis"),
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=self.config.colors.warning,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        f"{self.translation_manager.get_text('missing_values')}: {len(self.result.missing_fields)}",
                        size=16,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.colors.with_opacity(0.1, self.config.colors.warning),
                padding=40,
                border_radius=15,
                border=ft.border.all(2, self.config.colors.warning)
            )
        
        # Normal M-Score display
        score_color = self.result.get_risk_color()
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    self.translation_manager.get_text("m_score_title"),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.config.colors.primary,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                
                # Score display
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"{self.result.m_score:.3f}",
                            size=60,
                            weight=ft.FontWeight.BOLD,
                            color=score_color,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            self.translate_risk_level(self.result.risk_level),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=score_color,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=15),
                        ft.Text(
                            self.translate_interpretation(self.result.interpretation),
                            size=16,
                            color=ft.colors.GREY_600,
                            text_align=ft.TextAlign.CENTER
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.colors.WHITE,
                    padding=30,
                    border_radius=15,
                    border=ft.border.all(3, score_color)
                ),
                
                ft.Container(height=20),
                
                # Interpretation guide
                self.build_interpretation_guide()
                
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.colors.with_opacity(0.05, score_color),
            padding=30,
            border_radius=15,
            border=ft.border.all(1, ft.colors.with_opacity(0.3, score_color))
        )
    
    def build_interpretation_guide(self) -> ft.Control:
        """Build interpretation guide"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    self.translation_manager.get_text("interpretation_guide"),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=self.config.colors.primary
                ),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(Icons.CHECK_CIRCLE, color=self.config.colors.accent, size=20),
                    ft.Text(
                        self.translation_manager.get_text("guide_low"),
                        size=14,
                        color=ft.colors.GREY_700
                    )
                ]),
                ft.Container(height=5),
                ft.Row([
                    ft.Icon(Icons.WARNING, color=self.config.colors.danger, size=20),
                    ft.Text(
                        self.translation_manager.get_text("guide_high"),
                        size=14,
                        color=ft.colors.GREY_700
                    )
                ])
            ]),
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_300)
        )
    
    def build_ratios_section(self) -> ft.Control:
        """Build financial ratios section"""
        if not self.result.ratios:
            return ft.Container()
        
        ratio_descriptions = {
            "DSRI": self.translation_manager.get_text("dsri_desc"),
            "GMI": self.translation_manager.get_text("gmi_desc"),
            "AQI": self.translation_manager.get_text("aqi_desc"),
            "SGI": self.translation_manager.get_text("sgi_desc"),
            "DEPI": self.translation_manager.get_text("depi_desc"),
            "SGAI": self.translation_manager.get_text("sgai_desc"),
            "LVGI": self.translation_manager.get_text("lvgi_desc"),
            "TATA": self.translation_manager.get_text("tata_desc")
        }
        
        ratios_dict = self.result.ratios.to_dict()
        
        # Create ratio cards
        ratio_cards = []
        for name, value in ratios_dict.items():
            card = ft.Container(
                content=ft.Column([
                    ft.Text(
                        name,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=self.config.colors.primary,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        f"{value:.3f}",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.config.colors.secondary,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        ratio_descriptions.get(name, ""),
                        size=12,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.colors.WHITE,
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                width=280,
                height=140
            )
            ratio_cards.append(card)
        
        # Arrange cards in rows
        rows = []
        for i in range(0, len(ratio_cards), 4):
            row_cards = ratio_cards[i:i+4]
            rows.append(
                ft.Row(
                    row_cards,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    wrap=True
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    self.translation_manager.get_text("ratios_title"),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.config.colors.primary
                ),
                ft.Container(height=20),
                *rows
            ]),
            bgcolor=ft.colors.with_opacity(0.02, self.config.colors.primary),
            padding=20,
            border_radius=15,
            border=ft.border.all(1, ft.colors.with_opacity(0.2, self.config.colors.primary))
        )
    
    def build_data_section(self) -> ft.Control:
        """Build extracted financial data section"""
        # Create data table
        data_table = self.create_financial_data_table()
        
        # Copy button
        copy_button = ft.ElevatedButton(
            text=self.translation_manager.get_text("copy_data"),
            icon=Icons.COPY,
            on_click=lambda _: self.copy_callback(
                BeneishCalculator.format_financial_data_for_export(self.result.financial_data)
            ),
            style=ft.ButtonStyle(
                bgcolor=self.config.colors.accent,
                color=ft.colors.WHITE
            )
        )
        
        return ft.ExpansionTile(
            title=ft.Text(
                self.translation_manager.get_text("extracted_data"),
                size=20,
                weight=ft.FontWeight.BOLD,
                color=self.config.colors.primary
            ),
            subtitle=ft.Text(
                "Click to expand financial data details",
                size=14,
                color=ft.colors.GREY_600
            ),
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Row([copy_button], alignment=ft.MainAxisAlignment.END),
                        ft.Container(height=10),
                        data_table
                    ]),
                    padding=20
                )
            ],
            bgcolor=ft.colors.WHITE,
            collapsed_bgcolor=ft.colors.with_opacity(0.05, self.config.colors.primary)
        )
    
    def create_financial_data_table(self) -> ft.Control:
        """Create financial data table"""
        # Combine data from both years
        all_fields = set(self.result.financial_data.year_1_data.keys()) | set(self.result.financial_data.year_2_data.keys())
        
        rows = []
        for field in sorted(all_fields):
            year_1_val = self.result.financial_data.year_1_data.get(field, 0)
            year_2_val = self.result.financial_data.year_2_data.get(field, 0)
            
            # Highlight missing values
            year_1_color = ft.colors.RED_300 if year_1_val == 0 else ft.colors.BLACK
            year_2_color = ft.colors.RED_300 if year_2_val == 0 else ft.colors.BLACK
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(field.replace("_", " ").title(), size=14)),
                        ft.DataCell(ft.Text(f"{year_1_val:,.2f}", size=14, color=year_1_color)),
                        ft.DataCell(ft.Text(f"{year_2_val:,.2f}", size=14, color=year_2_color))
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Metric", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(self.translation_manager.get_text("year_1"), weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(self.translation_manager.get_text("year_2"), weight=ft.FontWeight.BOLD))
            ],
            rows=rows,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_300)
        )
    
    def translate_risk_level(self, risk_level: str) -> str:
        """Translate risk level"""
        if risk_level == "LOW RISK":
            return self.translation_manager.get_text("low_risk")
        elif risk_level == "HIGH RISK":
            return self.translation_manager.get_text("high_risk")
        return risk_level
    
    def translate_interpretation(self, interpretation: str) -> str:
        """Translate interpretation"""
        if "not likely" in interpretation:
            return self.translation_manager.get_text("low_risk_desc")
        elif "likely" in interpretation:
            return self.translation_manager.get_text("high_risk_desc")
        return interpretation