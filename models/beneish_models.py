# models/beneish_models.py - Data models and business logic
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from enum import Enum

class AnalysisStage(Enum):
    IDLE = "idle"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing" 
    CALCULATING = "calculating"
    COMPLETE = "complete"
    ERROR = "error"

# Pydantic model for LLM structured output
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
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "DSRI": self.dsri,
            "GMI": self.gmi, 
            "AQI": self.aqi,
            "SGI": self.sgi,
            "DEPI": self.depi,
            "SGAI": self.sgai,
            "LVGI": self.lvgi,
            "TATA": self.tata
        }

@dataclass 
class AnalysisResult:
    company_name: str
    financial_data: FinancialData
    ratios: Optional[BeneishRatios]
    m_score: Optional[float]
    risk_level: str
    interpretation: str
    missing_fields: List[str]
    success: bool
    error_message: Optional[str] = None
    
    def get_risk_color(self) -> str:
        """Get color code based on risk level"""
        return "#ef4444" if self.m_score and self.m_score > -1.78 else "#10b981"

class BeneishCalculator:
    """Core calculation logic for Beneish M-Score"""
    
    REQUIRED_FIELDS = [
        "revenue", "cost_of_goods_sold", "selling_general_admin_expense",
        "depreciation", "net_income_continuing_operations", "accounts_receivables", 
        "current_assets", "property_plant_equipment", "securities", "total_assets",
        "current_liabilities", "total_long_term_debt", "cash_flow_operations"
    ]
    
    @staticmethod
    def validate_data(year_1: Dict[str, float], year_2: Dict[str, float]) -> List[str]:
        """Validate that required fields are present and non-negative"""
        missing_fields = []
        
        for field in BeneishCalculator.REQUIRED_FIELDS:
            if field not in year_1 or year_1[field] is None:
                missing_fields.append(f"Year 1: {field}")
            if field not in year_2 or year_2[field] is None:
                missing_fields.append(f"Year 2: {field}")
                
        return missing_fields
    
    @staticmethod
    def calculate_ratios(year_1: Dict[str, float], year_2: Dict[str, float]) -> BeneishRatios:
        """Calculate the 8 Beneish M-Score ratios"""
        
        # Helper function to safely divide
        def safe_divide(numerator, denominator, default=1.0):
            return numerator / denominator if denominator != 0 else default
        
        # Days Sales in Receivables Index (DSRI)
        dsr_1 = safe_divide(year_1['accounts_receivables'], year_1['revenue'])  if year_1['revenue'] != 0 else 0
        dsr_2 = safe_divide(year_2['accounts_receivables'], year_2['revenue'])  if year_2['revenue'] != 0 else 0
        dsri = safe_divide(dsr_2, dsr_1)
        
        # Gross Margin Index (GMI)
        gross_margin_1 = safe_divide(year_1['revenue'] - year_1['cost_of_goods_sold'], year_1['revenue'])
        gross_margin_2 = safe_divide(year_2['revenue'] - year_2['cost_of_goods_sold'], year_2['revenue'])
        gmi = safe_divide(gross_margin_1, gross_margin_2)
        
        # Asset Quality Index (AQI)
        quality_assets_1 = year_1['current_assets'] + year_1['property_plant_equipment'] + year_1['securities']
        quality_assets_2 = year_2['current_assets'] + year_2['property_plant_equipment'] + year_2['securities']
        
        aqi_1 = 1 - safe_divide(quality_assets_1, year_1['total_assets'], 0)
        aqi_2 = 1 - safe_divide(quality_assets_2, year_2['total_assets'], 0)
        aqi = safe_divide(aqi_2, aqi_1)
        
        # Sales Growth Index (SGI)
        sgi = safe_divide(year_2['revenue'], year_1['revenue'])
        
        # Depreciation Index (DEPI)
        depr_rate_1 = safe_divide(year_1['depreciation'], 
                                 year_1['depreciation'] + year_1['property_plant_equipment'])
        depr_rate_2 = safe_divide(year_2['depreciation'],
                                 year_2['depreciation'] + year_2['property_plant_equipment'])
        depi = safe_divide(depr_rate_1, depr_rate_2)
        
        # SGA Expenses Index (SGAI)
        sga_rate_1 = safe_divide(year_1['selling_general_admin_expense'], year_1['revenue'])
        sga_rate_2 = safe_divide(year_2['selling_general_admin_expense'], year_2['revenue'])
        sgai = safe_divide(sga_rate_2, sga_rate_1)
        
        # Leverage Index (LVGI)
        leverage_1 = safe_divide(year_1['current_liabilities'] + year_1['total_long_term_debt'], 
                               year_1['total_assets'])
        leverage_2 = safe_divide(year_2['current_liabilities'] + year_2['total_long_term_debt'],
                               year_2['total_assets'])
        lvgi = safe_divide(leverage_2, leverage_1)
        
        # Total Accruals to Total Assets (TATA)
        income_before_extra = year_2['net_income_continuing_operations']
        tata = safe_divide(income_before_extra - year_2['cash_flow_operations'], 
                          year_2['total_assets'], 0)
        
        return BeneishRatios(dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata)
    
    @staticmethod
    def calculate_m_score(ratios: BeneishRatios) -> float:
        """Calculate the Beneish M-Score using the standard formula"""
        m_score = (-4.840 + 
                  0.920 * ratios.dsri + 
                  0.528 * ratios.gmi + 
                  0.404 * ratios.aqi +
                  0.892 * ratios.sgi + 
                  0.115 * ratios.depi - 
                  0.172 * ratios.sgai +
                  4.679 * ratios.tata - 
                  0.327 * ratios.lvgi)
        return m_score
    
    @staticmethod
    def interpret_score(m_score: float) -> tuple[str, str]:
        """Interpret the M-Score result"""
        if m_score < -1.78:
            return "LOW RISK", "Company is not likely to have manipulated their earnings"
        else:
            return "HIGH RISK", "Company is likely to have manipulated their earnings"
    
    @staticmethod
    def format_financial_data_for_export(financial_data: FinancialData) -> str:
        """Format financial data for TSV export"""
        headers = ["Metric", "Year 1", "Year 2"]
        rows = ["\t".join(headers)]
        
        # Combine all metrics
        all_fields = set(financial_data.year_1_data.keys()) | set(financial_data.year_2_data.keys())
        
        for field in sorted(all_fields):
            year_1_val = financial_data.year_1_data.get(field, 0)
            year_2_val = financial_data.year_2_data.get(field, 0)
            rows.append(f"{field}\t{year_1_val:,.2f}\t{year_2_val:,.2f}")
        
        return "\n".join(rows)