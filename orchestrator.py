from typing import Dict, Any, Callable, List
from state import VDRAnalysisState
from doc_parser import DocumentParser
from faiss_indexer import FAISSContractIndexer
from legal_agent import analyze_legal
from financial_agent import analyze_financial
from hr_agent import analyze_hr

class StateGraph:
    """
    Lightweight LangGraph-compatible state graph orchestrator.
    Manages state transitions, node execution, and execution DAG.
    """
    def __init__(self, state_schema):
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable] = {}
        self.edges: List[tuple] = []
        self.entry_point: str = ""

    def add_node(self, name: str, func: Callable):
        self.nodes[name] = func

    def add_edge(self, start: str, end: str):
        self.edges.append((start, end))

    def set_entry_point(self, name: str):
        self.entry_point = name

    def compile(self):
        return CompiledGraph(self)

class CompiledGraph:
    def __init__(self, graph: StateGraph):
        self.graph = graph

    def invoke(self, state: VDRAnalysisState) -> VDRAnalysisState:
        # Build adjacency mapping
        adj = {}
        for s, e in self.graph.edges:
            adj[s] = e

        current = self.graph.entry_point
        while current and current != "END":
            func = self.graph.nodes.get(current)
            if func:
                state = func(state)
            current = adj.get(current, "END")
            
        return state

def create_contract_swarm_graph() -> CompiledGraph:
    graph = StateGraph(VDRAnalysisState)
    indexer = FAISSContractIndexer()

    def index_vdr_node(state: VDRAnalysisState) -> VDRAnalysisState:
        # Ensure contract corpus is populated
        if not state.contracts and state.contract_text:
            state.contracts = {"Target_Contract": state.contract_text}
            
        # Index all contracts in FAISS
        indexer.index_contracts(state.contracts)
        return state

    def legal_node(state: VDRAnalysisState) -> VDRAnalysisState:
        return analyze_legal(state, indexer)

    def financial_node(state: VDRAnalysisState) -> VDRAnalysisState:
        return analyze_financial(state, indexer)

    def hr_node(state: VDRAnalysisState) -> VDRAnalysisState:
        return analyze_hr(state, indexer)

    def synthesis_node(state: VDRAnalysisState) -> VDRAnalysisState:
        high_count = sum(1 for r in state.risks if r.severity == "High")
        med_count = sum(1 for r in state.risks if r.severity == "Medium")
        low_count = sum(1 for r in state.risks if r.severity == "Low")
        
        num_contracts = len(state.contracts) if state.contracts else 1
        risk_level = "ELEVATED" if high_count > 0 else ("MODERATE" if med_count > 0 else "LOW")

        # Per contract risk counts
        contract_breakdown = {}
        for r in state.risks:
            cname = r.contract_name or "Target Contract"
            contract_breakdown[cname] = contract_breakdown.get(cname, 0) + 1

        state.portfolio_metrics = {
            "total_contracts_audited": num_contracts,
            "total_liabilities_flagged": len(state.risks),
            "high_severity_count": high_count,
            "medium_severity_count": med_count,
            "low_severity_count": low_count,
            "overall_portfolio_risk": risk_level,
            "contract_breakdown": contract_breakdown,
            "workstream_breakdown": {
                "Legal": sum(1 for r in state.risks if r.category == "Legal"),
                "Financial": sum(1 for r in state.risks if r.category == "Financial"),
                "HR": sum(1 for r in state.risks if r.category == "HR")
            }
        }

        state.executive_summary = (
            f"M&A Due Diligence Executive Summary: Portfolio review of {num_contracts} VDR contract(s) completed with {risk_level} risk profile. "
            f"Total Liabilities Flagged: {len(state.risks)} (High Severity: {high_count}, Medium Severity: {med_count}, Low Severity: {low_count}). "
            f"Immediate executive legal, financial, and human capital review recommended prior to definitive deal closure."
        )
        return state

    graph.add_node("index_vdr", index_vdr_node)
    graph.add_node("legal_agent", legal_node)
    graph.add_node("financial_agent", financial_node)
    graph.add_node("hr_agent", hr_node)
    graph.add_node("partner_synthesizer", synthesis_node)

    graph.set_entry_point("index_vdr")
    graph.add_edge("index_vdr", "legal_agent")
    graph.add_edge("legal_agent", "financial_agent")
    graph.add_edge("financial_agent", "hr_agent")
    graph.add_edge("hr_agent", "partner_synthesizer")
    graph.add_edge("partner_synthesizer", "END")

    return graph.compile()

# Global compiled LangGraph orchestrator
_compiled_swarm = create_contract_swarm_graph()

def run_contract_swarm(state: VDRAnalysisState) -> VDRAnalysisState:
    """
    Executes the multi-agent swarm state graph on the provided VDR state.
    """
    return _compiled_swarm.invoke(state)

def run_vdr_zip_audit(zip_source, package_name: str = "VDR Package") -> VDRAnalysisState:
    """
    Primary Key Deliverable: Ingests a zip file of corporate contracts,
    parses each contract, indexes with FAISS, and executes the multi-agent
    swarm to produce a unified JSON risk matrix and executive summary.
    """
    parser = DocumentParser()
    extracted_contracts = parser.parse_vdr_zip(zip_source)
    
    state = VDRAnalysisState(
        vdr_package_name=package_name,
        contracts=extracted_contracts,
        contract_text="\n\n".join(extracted_contracts.values()),
        risks=[]
    )
    
    return run_contract_swarm(state)
