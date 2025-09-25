from typing import Dict, Any, Optional
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from models.beneish_models import AnalysisResult
from models.translation import TranslationManager

class ExportService:
    """Service for exporting Beneish M-Score analysis results to PDF and Excel formats."""
    
    def __init__(self, translation_manager: TranslationManager):
        self.translation_manager = translation_manager
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for PDF generation."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkgreen
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_LEFT
        )
    
    def export_to_pdf(self, result: AnalysisResult, file_path: str, company_name: str = "") -> bool:
        """Export Beneish analysis results to PDF format."""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Title
            title = self.translation_manager.get_text("results_title")
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 20))
            
            # Company name if provided
            if company_name:
                company_title = f"{self.translation_manager.get_text('company_name')}: {company_name}"
                story.append(Paragraph(company_title, self.subtitle_style))
                story.append(Spacer(1, 15))
            
            # Generation date
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"Generated: {date_str}", self.normal_style))
            story.append(Spacer(1, 20))
            
            # M-Score Summary
            story.append(Paragraph(self.translation_manager.get_text("m_score_title"), self.subtitle_style))
            
            m_score_data = [
                ["M-Score", f"{result.m_score:.3f}"],
                ["Risk Level", self.translation_manager.get_text("high_risk" if result.m_score and result.m_score > -1.78 else "low_risk")],
                ["Interpretation", self.translation_manager.get_text("high_risk_desc" if result.m_score and result.m_score > -1.78 else "low_risk_desc")]
            ]
            
            m_score_table = Table(m_score_data, colWidths=[1.2*inch, 3.8*inch])
            m_score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(m_score_table)
            story.append(Spacer(1, 30))
            
            # Ratios Analysis
            if result.ratios:
                story.append(Paragraph(self.translation_manager.get_text("ratios_title"), self.subtitle_style))
                
                ratios_data = [["Ratio", "Value", "Description"]]
                
                ratio_names = {
                    "DSRI": "dsri",
                    "GMI": "gmi", 
                    "AQI": "aqi",
                    "SGI": "sgi",
                    "DEPI": "depi",
                    "SGAI": "sgai",
                    "LVGI": "lvgi",
                    "TATA": "tata"
                }
                
                ratios_dict = result.ratios.to_dict()
                for ratio_key, ratio_value in ratios_dict.items():
                    if ratio_key in ratio_names:
                        ratio_name = self.translation_manager.get_text(ratio_names[ratio_key])
                        ratio_desc = self.translation_manager.get_text(f"{ratio_key.lower()}_desc")
                        ratios_data.append([ratio_name, f"{ratio_value:.3f}", ratio_desc])
                
                ratios_table = Table(ratios_data, colWidths=[3.5*inch, 1*inch, 3.5*inch])
                ratios_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(ratios_table)
                story.append(Spacer(1, 30))
            
            # Financial Data
            if result.financial_data:
                story.append(Paragraph(self.translation_manager.get_text("extracted_data"), self.subtitle_style))
                
                # Create financial data table
                financial_data = []
                financial_data.append(["Metric", self.translation_manager.get_text("year_1"), self.translation_manager.get_text("year_2")])
                
                # Add financial metrics
                metrics = [
                    ("revenue", "Revenue"),
                    ("cost_of_goods_sold", "Cost of Goods Sold"),
                    ("selling_general_admin_expense", "SG&A Expenses"),
                    ("depreciation", "Depreciation"),
                    ("net_income_continuing_operations", "Net Income"),
                    ("accounts_receivables", "Accounts Receivables"),
                    ("current_assets", "Current Assets"),
                    ("property_plant_equipment", "PP&E"),
                    ("total_assets", "Total Assets"),
                    ("current_liabilities", "Current Liabilities"),
                    ("total_long_term_debt", "Long-term Debt"),
                    ("cash_flow_operations", "Cash Flow from Operations")
                ]
                
                for metric_key, metric_label in metrics:
                    year1_val = result.financial_data.year_1_data.get(metric_key, 0)
                    year2_val = result.financial_data.year_2_data.get(metric_key, 0)
                    translated_label = self.translation_manager.get_text(metric_key)
                    financial_data.append([translated_label, f"{year1_val:,.0f}", f"{year2_val:,.0f}"])
                
                financial_table = Table(financial_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
                financial_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(financial_table)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def export_to_excel(self, result: AnalysisResult, file_path: str, company_name: str = "") -> bool:
        """Export Beneish analysis results to Excel format."""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                # Summary Sheet
                summary_data = {
                    'Metric': ['Company Name', 'M-Score', 'Risk Level', 'Analysis Date'],
                    'Value': [
                        company_name or 'N/A',
                        f"{result.m_score:.3f}",
                        self.translation_manager.get_text("high_risk" if result.m_score and result.m_score > -1.78 else "low_risk"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Ratios Sheet
                if result.ratios:
                    ratios_data = {
                        'Ratio': [],
                        'Value': [],
                        'Description': []
                    }
                    
                    ratio_names = {
                        "DSRI": "dsri",
                        "GMI": "gmi",
                        "AQI": "aqi", 
                        "SGI": "sgi",
                        "DEPI": "depi",
                        "SGAI": "sgai",
                        "LVGI": "lvgi",
                        "TATA": "tata"
                    }
                    
                    ratios_dict = result.ratios.to_dict()
                    for ratio_key, ratio_value in ratios_dict.items():
                        if ratio_key in ratio_names:
                            ratios_data['Ratio'].append(self.translation_manager.get_text(ratio_names[ratio_key]))
                            ratios_data['Value'].append(ratio_value)
                            ratios_data['Description'].append(self.translation_manager.get_text(f"{ratio_key.lower()}_desc"))
                    
                    ratios_df = pd.DataFrame(ratios_data)
                    ratios_df.to_excel(writer, sheet_name='Ratios Analysis', index=False)
                
                # Financial Data Sheet
                if result.financial_data:
                    financial_data = {
                        'Metric': [],
                        self.translation_manager.get_text("year_1"): [],
                        self.translation_manager.get_text("year_2"): []
                    }
                    
                    metrics = [
                        ("revenue", "Revenue"),
                        ("cost_of_goods_sold", "Cost of Goods Sold"),
                        ("selling_general_admin_expense", "SG&A Expenses"),
                        ("depreciation", "Depreciation"),
                        ("net_income_continuing_operations", "Net Income"),
                        ("accounts_receivables", "Accounts Receivables"),
                        ("current_assets", "Current Assets"),
                        ("property_plant_equipment", "PP&E"),
                        ("total_assets", "Total Assets"),
                        ("current_liabilities", "Current Liabilities"),
                        ("total_long_term_debt", "Long-term Debt"),
                        ("cash_flow_operations", "Cash Flow from Operations")
                    ]
                    
                    for metric_key, metric_label in metrics:
                        year1_val = result.financial_data.year_1_data.get(metric_key, 0)
                        year2_val = result.financial_data.year_2_data.get(metric_key, 0)
                        translated_label = self.translation_manager.get_text(metric_key)
                        
                        financial_data['Metric'].append(translated_label)
                        financial_data[self.translation_manager.get_text("year_1")].append(year1_val)
                        financial_data[self.translation_manager.get_text("year_2")].append(year2_val)
                    
                    financial_df = pd.DataFrame(financial_data)
                    financial_df.to_excel(writer, sheet_name='Financial Data', index=False)
            
            return True
            
        except Exception as e:
            print(f"Error generating Excel: {e}")
            return False
