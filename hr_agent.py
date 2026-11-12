from typing import Optional
from state import VDRAnalysisState, RiskItem
from faiss_indexer import FAISSContractIndexer

def analyze_hr(state: VDRAnalysisState, indexer: Optional[FAISSContractIndexer] = None) -> VDRAnalysisState:
    found_risks = list(state.risks)
    
    contract_map = state.contracts if state.contracts else {"Target_Contract": state.contract_text}
    
    for doc_name, text in contract_map.items():
        lower_text = text.lower()
        
        # Non-compete and restrictive covenants
        if "non-compete" in lower_text or "restrictive covenant" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="HR",
                severity="Medium",
                clause_reference="Restrictive Covenants",
                description="Key employee non-compete clauses may restrict post-acquisition deployment and hiring flexibility.",
                mitigation="Review jurisdictional enforceability (FTC / local state laws) and re-execute tailored non-solicitation covenants."
            ))
            
        # Severance and golden parachutes
        if "severance" in lower_text or "golden parachute" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="HR",
                severity="High",
                clause_reference="Executive Compensation / Severance",
                description="Significant severance or retention acceleration obligations triggered upon merger execution.",
                mitigation="Incorporate executive change-of-control liabilities into purchase price consideration and escrow reserves."
            ))

        # Accelerated vesting
        if "accelerated vesting" in lower_text or "retention bonus" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="HR",
                severity="High",
                clause_reference="Single-Trigger Accelerated Equity Vesting",
                description="Automatic 100% equity acceleration upon change of control undermines post-closing key talent retention.",
                mitigation="Negotiate double-trigger acceleration (change of control plus involuntary termination within 12 months)."
            ))

        # Key person dependency
        if "key man" in lower_text or "key person" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="HR",
                severity="High",
                clause_reference="Key Person Operational Dependency",
                description="Contract terminable upon departure of designated personnel, creating executive retention vulnerability.",
                mitigation="Execute multi-year employment agreements with key executives prior to definitive agreement execution."
            ))
            
    state.risks = found_risks
    return state
