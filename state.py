from typing import List, Dict, Any
from pydantic import BaseModel, Field

class RiskItem(BaseModel):
    contract_name: str = Field(default="", description="Source contract filename in VDR package")
    category: str = Field(description="Legal, Financial, or HR")
    severity: str = Field(description="High, Medium, or Low")
    clause_reference: str = Field(description="Specific section or text snippet triggering the risk")
    description: str = Field(description="Explanation of the liability or risk")
    mitigation: str = Field(default="", description="Recommended EY advisory mitigation or negotiation strategy")

class VDRAnalysisState(BaseModel):
    vdr_package_name: str = Field(default="Corporate VDR Contract Batch", description="Name of VDR package or zip archive")
    contracts: Dict[str, str] = Field(default_factory=dict, description="Map of contract filename to raw contract text")
    contract_text: str = Field(default="", description="Aggregated or single contract text")
    risks: List[RiskItem] = Field(default_factory=list, description="Aggregated risk items found by agents across all contracts")
    executive_summary: str = Field(default="", description="Unified executive summary for M&A partners")
    portfolio_metrics: Dict[str, Any] = Field(default_factory=dict, description="High-level portfolio and workstream metrics")
