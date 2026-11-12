from typing import Optional
from state import VDRAnalysisState, RiskItem
from faiss_indexer import FAISSContractIndexer

def analyze_legal(state: VDRAnalysisState, indexer: Optional[FAISSContractIndexer] = None) -> VDRAnalysisState:
    found_risks = list(state.risks)
    
    # Contract corpus map: multi-contract package or single contract fallback
    contract_map = state.contracts if state.contracts else {"Target_Contract": state.contract_text}
    
    for doc_name, text in contract_map.items():
        lower_text = text.lower()
        
        # Indemnification / Hold Harmless
        if "indemnification" in lower_text or "hold harmless" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Legal",
                severity="High",
                clause_reference="Indemnification / Liability Clause",
                description="Broad indemnification obligations detected; potential open-ended liability post-acquisition.",
                mitigation="Negotiate a bilateral liability cap tied to 10-15% of contract value and exclude consequential damages."
            ))
            
        # Change of Control
        if "change of control" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Legal",
                severity="Medium",
                clause_reference="Change of Control Provision",
                description="Trigger events or third-party consent requirements upon corporate acquisition identified.",
                mitigation="Obtain formal counterparty consent waivers prior to closing or structure deal via asset-purchase carveout."
            ))

        # Unlimited Liability
        if "unlimited liability" in lower_text or "uncapped" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Legal",
                severity="High",
                clause_reference="Uncapped Liability Provision",
                description="Absence of financial limitation of liability exposes acquiring entity to catastrophic exposure.",
                mitigation="Insist on customary aggregate liability caps and carve out standard gross negligence exceptions."
            ))

        # Exclusivity / MFN
        if "exclusivity" in lower_text or "most favored nation" in lower_text or "mfn" in lower_text:
            found_risks.append(RiskItem(
                contract_name=doc_name,
                category="Legal",
                severity="Medium",
                clause_reference="Exclusivity / MFN Covenant",
                description="Restrictive commercial covenant limits pricing autonomy and market distribution across combined entities.",
                mitigation="Insert affiliate carve-out clause to ensure acquired restrictions do not bind parent entities."
            ))
            
    state.risks = found_risks
    return state
