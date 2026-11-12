from typing import Optional
from state import VDRAnalysisState, RiskItem
from faiss_indexer import FAISSContractIndexer

def analyze_financial(state: VDRAnalysisState, indexer: Optional[FAISSContractIndexer] = None) -> VDRAnalysisState:
    found_risks = list(state.risks)
    
    contract_map = state.contracts if state.contracts else {"Target_Contract": state.contract_text}
    
    for doc_name, text in contract_map.items():
        lower_text = text.lower()
        
        # Penalties / Liquidated Damages
        if "penalty" in lower_text or "liquidated damages" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Financial",
                severity="High",
                clause_reference="Penalties / Damages Clause",
                description="Severe financial penalties or liquidated damages clauses present for timeline breach.",
                mitigation="Cap liquidated damages at realistic pre-estimated operational damages and convert to cure-period remediation."
            ))
            
        # Extended Payment Terms
        if "net 90" in lower_text or "net 120" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Financial",
                severity="Medium",
                clause_reference="Payment Terms",
                description="Extended payment terms (Net 90+) detected, which may impact working capital post-merger.",
                mitigation="Align payment terms to standard corporate treasury policy (Net 30/45) during contract novation."
            ))

        # Minimum Commitments
        if "minimum commitment" in lower_text or "take or pay" in lower_text or "minimum purchase" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Financial",
                severity="High",
                clause_reference="Minimum Purchase / Take-or-Pay Obligation",
                description="Mandatory annual volume commitments generate fixed overhead regardless of actual post-merger integration volume.",
                mitigation="Audit historical run-rates and renegotiate minimums based on actual post-closing consolidation forecasts."
            ))

        # Compounding Late Penalties
        if "compounding" in lower_text or "late payment fee" in lower_text or "interest fee" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Financial",
                severity="Low",
                clause_reference="Compounding Default Interest",
                description="Above-market interest accrual formulas on contested or delayed commercial billings.",
                mitigation="Revise late interest to benchmark policy rate (SOFR + 1.5%) non-compounding."
            ))
            
    state.risks = found_risks
    return state
