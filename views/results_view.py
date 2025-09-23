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
        """Build financial ratios section with detailed formula calculations"""
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
        
        # Create enhanced ratio cards with formula calculations
        ratio_cards = []
        for name, value in ratios_dict.items():
            formula_details = self._get_formula_details(name)
            
            card = ft.Container(
                content=ft.Column([
                    ft.Text(
                        self.translation_manager.get_text(name.lower()) if name.lower() in ['dsri', 'gmi', 'aqi', 'sgi', 'depi', 'sgai', 'lvgi', 'tata'] else name,
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
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton(
                                icon=ft.icons.HELP_OUTLINE,
                                icon_size=24,
                                tooltip=formula_details['tooltip'],
                                icon_color=self.config.colors.accent,
                                on_click=lambda e, details=formula_details: self._show_formula_dialog(e, details)
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        margin=ft.margin.only(top=5)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.colors.WHITE,
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.GREY_300),
                width=320,
                height=190
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
    
    def _get_formula_details(self, ratio_name: str) -> dict:
        """Get formula and calculation details for a specific ratio"""
        year_1 = self.result.financial_data.year_1_data
        year_2 = self.result.financial_data.year_2_data
        
        def safe_divide(a, b, default=1):
            return a / b if b != 0 else default
        
        def format_number(num):
            return f"{num:,.0f}" if abs(num) >= 1 else f"{num:.3f}"
        
        if ratio_name == "DSRI":
            # Days Sales in Receivables Index
            dsr_1 = safe_divide(year_1.get('accounts_receivables', 0), year_1.get('revenue', 1)) * 365
            dsr_2 = safe_divide(year_2.get('accounts_receivables', 0), year_2.get('revenue', 1)) * 365
            
            return {
                "formula": "DSRI = (AR₂/Sales₂ × 365) ÷ (AR₁/Sales₁ × 365)",
                "calculation": f"DSRI = ({format_number(year_2.get('accounts_receivables', 0))}/{format_number(year_2.get('revenue', 1))} × 365) ÷ ({format_number(year_1.get('accounts_receivables', 0))}/{format_number(year_1.get('revenue', 1))} × 365)\n= {dsr_2:.1f} ÷ {dsr_1:.1f} = {safe_divide(dsr_2, dsr_1):.3f}",
                "tooltip": self.translation_manager.get_text("dsri_tooltip_description") + f"\n\nDSRI = (AR₂/Sales₂ × 365) ÷ (AR₁/Sales₁ × 365)\n= {dsr_2:.1f} ÷ {dsr_1:.1f} = {safe_divide(dsr_2, dsr_1):.3f}"
            }
        
        elif ratio_name == "GMI":
            # Gross Margin Index
            gm_1 = safe_divide(year_1.get('revenue', 0) - year_1.get('cost_of_goods_sold', 0), year_1.get('revenue', 1))
            gm_2 = safe_divide(year_2.get('revenue', 0) - year_2.get('cost_of_goods_sold', 0), year_2.get('revenue', 1))
            
            return {
                "formula": "GMI = Gross Margin₁ ÷ Gross Margin₂",
                "calculation": f"GMI = {gm_1:.3f} ÷ {gm_2:.3f} = {safe_divide(gm_1, gm_2):.3f}\nGross Margin₁ = ({format_number(year_1.get('revenue', 0))} - {format_number(year_1.get('cost_of_goods_sold', 0))}) ÷ {format_number(year_1.get('revenue', 1))}\nGross Margin₂ = ({format_number(year_2.get('revenue', 0))} - {format_number(year_2.get('cost_of_goods_sold', 0))}) ÷ {format_number(year_2.get('revenue', 1))}",
                "tooltip": self.translation_manager.get_text("gmi_tooltip_description") + f"\n\nGMI = Gross Margin₁ ÷ Gross Margin₂\n\nGMI = {gm_1:.3f} ÷ {gm_2:.3f} = {safe_divide(gm_1, gm_2):.3f}\nGross Margin₁ = ({format_number(year_1.get('revenue', 0))} - {format_number(year_1.get('cost_of_goods_sold', 0))}) ÷ {format_number(year_1.get('revenue', 1))}\nGross Margin₂ = ({format_number(year_2.get('revenue', 0))} - {format_number(year_2.get('cost_of_goods_sold', 0))}) ÷ {format_number(year_2.get('revenue', 1))}"
            }
        
        elif ratio_name == "AQI":
            # Asset Quality Index
            qa_1 = year_1.get('current_assets', 0) + year_1.get('property_plant_equipment', 0) + year_1.get('securities', 0)
            qa_2 = year_2.get('current_assets', 0) + year_2.get('property_plant_equipment', 0) + year_2.get('securities', 0)
            aqi_1 = 1 - safe_divide(qa_1, year_1.get('total_assets', 1), 0)
            aqi_2 = 1 - safe_divide(qa_2, year_2.get('total_assets', 1), 0)
            
            return {
                "formula": "AQI = (1 - Quality Assets₂/Total Assets₂) ÷ (1 - Quality Assets₁/Total Assets₁)",
                "calculation": f"AQI = {aqi_2:.3f} ÷ {aqi_1:.3f} = {safe_divide(aqi_2, aqi_1):.3f}\nQuality Assets₂ = {format_number(qa_2)}\nQuality Assets₁ = {format_number(qa_1)}",
                "tooltip": self.translation_manager.get_text("aqi_tooltip_description") + f"\n\nAQI = (1 - Quality Assets₂/Total Assets₂) ÷ (1 - Quality Assets₁/Total Assets₁)\n\nAQI = {aqi_2:.3f} ÷ {aqi_1:.3f} = {safe_divide(aqi_2, aqi_1):.3f}\nQuality Assets₂ = {format_number(qa_2)}\nQuality Assets₁ = {format_number(qa_1)}"
            }
        
        elif ratio_name == "SGI":
            # Sales Growth Index
            return {
                "formula": "SGI = Sales₂ ÷ Sales₁",
                "calculation": f"SGI = {format_number(year_2.get('revenue', 0))} ÷ {format_number(year_1.get('revenue', 1))} = {safe_divide(year_2.get('revenue', 0), year_1.get('revenue', 1)):.3f}",
                "tooltip": self.translation_manager.get_text("sgi_tooltip_description") + f"\n\nSGI = Sales₂ ÷ Sales₁\n\nSGI = {format_number(year_2.get('revenue', 0))} ÷ {format_number(year_1.get('revenue', 1))} = {safe_divide(year_2.get('revenue', 0), year_1.get('revenue', 1)):.3f}"
            }
        
        elif ratio_name == "DEPI":
            # Depreciation Index
            depr_rate_1 = safe_divide(year_1.get('depreciation', 0), year_1.get('depreciation', 0) + year_1.get('property_plant_equipment', 1))
            depr_rate_2 = safe_divide(year_2.get('depreciation', 0), year_2.get('depreciation', 0) + year_2.get('property_plant_equipment', 1))
            
            return {
                "formula": "DEPI = Depreciation Rate₁ ÷ Depreciation Rate₂",
                "calculation": f"DEPI = {depr_rate_1:.3f} ÷ {depr_rate_2:.3f} = {safe_divide(depr_rate_1, depr_rate_2):.3f}\nDepr Rate₁ = {format_number(year_1.get('depreciation', 0))} ÷ ({format_number(year_1.get('depreciation', 0))} + {format_number(year_1.get('property_plant_equipment', 1))})\nDepr Rate₂ = {format_number(year_2.get('depreciation', 0))} ÷ ({format_number(year_2.get('depreciation', 0))} + {format_number(year_2.get('property_plant_equipment', 1))})",
                "tooltip": self.translation_manager.get_text("depi_tooltip_description") + f"\n\nDEPI = Depreciation Rate₁ ÷ Depreciation Rate₂\n\nDEPI = {depr_rate_1:.3f} ÷ {depr_rate_2:.3f} = {safe_divide(depr_rate_1, depr_rate_2):.3f}\nDepr Rate₁ = {format_number(year_1.get('depreciation', 0))} ÷ ({format_number(year_1.get('depreciation', 0))} + {format_number(year_1.get('property_plant_equipment', 1))})\nDepr Rate₂ = {format_number(year_2.get('depreciation', 0))} ÷ ({format_number(year_2.get('depreciation', 0))} + {format_number(year_2.get('property_plant_equipment', 1))})"
            }
        
        elif ratio_name == "SGAI":
            # SGA Expenses Index
            sga_rate_1 = safe_divide(year_1.get('selling_general_admin_expense', 0), year_1.get('revenue', 1))
            sga_rate_2 = safe_divide(year_2.get('selling_general_admin_expense', 0), year_2.get('revenue', 1))
            
            return {
                "formula": "SGAI = SGA Rate₂ ÷ SGA Rate₁",
                "calculation": f"SGAI = {sga_rate_2:.3f} ÷ {sga_rate_1:.3f} = {safe_divide(sga_rate_2, sga_rate_1):.3f}\nSGA Rate₂ = {format_number(year_2.get('selling_general_admin_expense', 0))} ÷ {format_number(year_2.get('revenue', 1))}\nSGA Rate₁ = {format_number(year_1.get('selling_general_admin_expense', 0))} ÷ {format_number(year_1.get('revenue', 1))}",
                "tooltip": self.translation_manager.get_text("sgai_tooltip_description") + f"\n\nSGAI = SGA Rate₂ ÷ SGA Rate₁\n\nSGAI = {sga_rate_2:.3f} ÷ {sga_rate_1:.3f} = {safe_divide(sga_rate_2, sga_rate_1):.3f}\nSGA Rate₂ = {format_number(year_2.get('selling_general_admin_expense', 0))} ÷ {format_number(year_2.get('revenue', 1))}\nSGA Rate₁ = {format_number(year_1.get('selling_general_admin_expense', 0))} ÷ {format_number(year_1.get('revenue', 1))}"
            }
        
        elif ratio_name == "LVGI":
            # Leverage Index
            leverage_1 = safe_divide(year_1.get('current_liabilities', 0) + year_1.get('total_long_term_debt', 0), year_1.get('total_assets', 1))
            leverage_2 = safe_divide(year_2.get('current_liabilities', 0) + year_2.get('total_long_term_debt', 0), year_2.get('total_assets', 1))
            
            return {
                "formula": "LVGI = Leverage₂ ÷ Leverage₁",
                "calculation": f"LVGI = {leverage_2:.3f} ÷ {leverage_1:.3f} = {safe_divide(leverage_2, leverage_1):.3f}\nLeverage₂ = ({format_number(year_2.get('current_liabilities', 0))} + {format_number(year_2.get('total_long_term_debt', 0))}) ÷ {format_number(year_2.get('total_assets', 1))}\nLeverage₁ = ({format_number(year_1.get('current_liabilities', 0))} + {format_number(year_1.get('total_long_term_debt', 0))}) ÷ {format_number(year_1.get('total_assets', 1))}",
                "tooltip": self.translation_manager.get_text("lvgi_tooltip_description") + f"\n\nLVGI = Leverage₂ ÷ Leverage₁\n\nLVGI = {leverage_2:.3f} ÷ {leverage_1:.3f} = {safe_divide(leverage_2, leverage_1):.3f}\nLeverage₂ = ({format_number(year_2.get('current_liabilities', 0))} + {format_number(year_2.get('total_long_term_debt', 0))}) ÷ {format_number(year_2.get('total_assets', 1))}\nLeverage₁ = ({format_number(year_1.get('current_liabilities', 0))} + {format_number(year_1.get('total_long_term_debt', 0))}) ÷ {format_number(year_1.get('total_assets', 1))}"
            }
        
        elif ratio_name == "TATA":
            # Total Accruals to Total Assets
            income_before_extra = year_2.get('net_income_continuing_operations', 0)
            cash_flow_ops = year_2.get('cash_flow_operations', 0)
            total_assets = year_2.get('total_assets', 1)
            
            return {
                "formula": "TATA = (Net Income - Cash Flow from Operations) ÷ Total Assets",
                "calculation": f"TATA = ({format_number(income_before_extra)} - {format_number(cash_flow_ops)}) ÷ {format_number(total_assets)}\n= {format_number(income_before_extra - cash_flow_ops)} ÷ {format_number(total_assets)} = {safe_divide(income_before_extra - cash_flow_ops, total_assets, 0):.3f}",
                "tooltip": self.translation_manager.get_text("tata_tooltip_description") + f"\n\nTATA = (Net Income - Cash Flow from Operations) ÷ Total Assets\n\nTATA = ({format_number(income_before_extra)} - {format_number(cash_flow_ops)}) ÷ {format_number(total_assets)}\n= {format_number(income_before_extra - cash_flow_ops)} ÷ {format_number(total_assets)} = {safe_divide(income_before_extra - cash_flow_ops, total_assets, 0):.3f}"
            }
        
        return {
            "formula": "Formula not available",
            "calculation": "Calculation details not available",
            "tooltip": "Formula not available\n\nCalculation details not available"[:100] + "..."
        }
    
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
                self.translation_manager.get_text("expand_data_tooltip"),
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
                        ft.DataCell(ft.Text(
                            self.translation_manager.get_text(field) if field in self.translation_manager.translations[self.translation_manager.current_language] else field.replace("_", " ").title(), 
                            size=14
                        )),
                        ft.DataCell(ft.Text(f"{year_1_val:,.2f}", size=14, color=year_1_color)),
                        ft.DataCell(ft.Text(f"{year_2_val:,.2f}", size=14, color=year_2_color))
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(self.translation_manager.get_text("metric_column"), weight=ft.FontWeight.BOLD)),
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
    
    def _show_formula_dialog(self, e, formula_details: dict):
        """Show formula details in a dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(self.translation_manager.get_text("formula_calc_details"), weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Formula:",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=self.config.colors.primary
                    ),
                    ft.Text(
                        formula_details["formula"],
                        size=12,
                        color=ft.colors.GREY_800,
                        selectable=True
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Calculation:",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=self.config.colors.primary
                    ),
                    ft.Text(
                        formula_details["calculation"],
                        size=12,
                        color=ft.colors.GREY_800,
                        selectable=True
                    )
                ], spacing=5),
                width=500,
                height=300
            ),
            actions=[
                ft.TextButton(
                    self.translation_manager.get_text("close_button"),
                    on_click=lambda _: self.page.close(dialog)
                )
            ]
        )
        
        self.page.open(dialog)
        self.page.update()