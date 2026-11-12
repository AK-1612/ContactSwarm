import os
import unittest
import glob
from state import VDRAnalysisState, RiskItem
from doc_parser import DocumentParser
from faiss_indexer import FAISSContractIndexer
from legal_agent import analyze_legal
from financial_agent import analyze_financial
from hr_agent import analyze_hr
from orchestrator import run_contract_swarm, run_vdr_zip_audit
from server import app, AnalysisRequest, ZipAnalysisRequest, analyze_contract, analyze_vdr_zip
from streamlit.testing.v1 import AppTest

class TestContractSwarmPipeline(unittest.TestCase):

    def test_state_and_risk_model(self):
        risk = RiskItem(
            contract_name="Master_Agreement.pdf",
            category="Legal",
            severity="High",
            clause_reference="Indemnification",
            description="Broad liability exposure.",
            mitigation="Cap exposure at 10% deal value."
        )
        self.assertEqual(risk.contract_name, "Master_Agreement.pdf")
        self.assertEqual(risk.category, "Legal")
        self.assertEqual(risk.severity, "High")
        self.assertEqual(risk.mitigation, "Cap exposure at 10% deal value.")
        
        state = VDRAnalysisState(contracts={"Master_Agreement.pdf": "sample text"}, risks=[risk])
        dumped = state.model_dump()
        self.assertEqual(len(dumped["risks"]), 1)
        self.assertIn("Master_Agreement.pdf", dumped["contracts"])

    def test_faiss_indexer(self):
        indexer = FAISSContractIndexer()
        contracts = {
            "ContractA.pdf": "SECTION 4.1 INDEMNIFICATION. Target indemnifies Buyer against all claims.",
            "ContractB.pdf": "SECTION 9.2 LIQUIDATED DAMAGES. Penalty fee of $500,000 for delay."
        }
        num_indexed = indexer.index_contracts(contracts)
        self.assertGreaterEqual(num_indexed, 2)
        
        # Test semantic search
        results = indexer.search("indemnification liability", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("ContractA.pdf", results[0]["contract_name"])

    def test_specialized_agents(self):
        contracts = {
            "Doc1.pdf": "Indemnification and hold harmless obligations. Change of control consent.",
            "Doc2.pdf": "Liquidated damages penalty and Net 120 credit terms.",
            "Doc3.pdf": "Golden parachute severance and non-compete covenants."
        }
        state = VDRAnalysisState(contracts=contracts)
        
        state = analyze_legal(state)
        self.assertTrue(any(r.category == "Legal" and r.severity == "High" for r in state.risks))
        
        state = analyze_financial(state)
        self.assertTrue(any(r.category == "Financial" and r.severity == "High" for r in state.risks))
        
        state = analyze_hr(state)
        self.assertTrue(any(r.category == "HR" and r.severity == "High" for r in state.risks))

    def test_orchestrator_and_zip_ingestion(self):
        zip_path = "vdr_docs/VDR_Corporate_Contracts_Package.zip"
        self.assertTrue(os.path.exists(zip_path), f"ZIP package {zip_path} must exist")
        
        state = run_vdr_zip_audit(zip_path, package_name="VDR_Corporate_Contracts_Package.zip")
        self.assertGreaterEqual(len(state.contracts), 3)
        self.assertGreaterEqual(len(state.risks), 10)
        self.assertIn("M&A Due Diligence Executive Summary", state.executive_summary)
        self.assertIn("total_contracts_audited", state.portfolio_metrics)
        self.assertEqual(state.portfolio_metrics["total_contracts_audited"], 3)

    def test_fastapi_server_endpoints(self):
        sample_path = "vdr_docs/Project_Horizon_Merger_Agreement.pdf"
        self.assertTrue(os.path.exists(sample_path))
        res_single = analyze_contract(AnalysisRequest(pdf_path=sample_path))
        self.assertEqual(res_single["status"], "success")

        zip_path = "vdr_docs/VDR_Corporate_Contracts_Package.zip"
        res_zip = analyze_vdr_zip(ZipAnalysisRequest(zip_path=zip_path))
        self.assertEqual(res_zip["status"], "success")
        self.assertEqual(res_zip["portfolio_metrics"]["total_contracts_audited"], 3)
        self.assertGreaterEqual(len(res_zip["risk_matrix"]), 10)

    def test_streamlit_app_execution(self):
        at = AppTest.from_file("app.py", default_timeout=30)
        at.run()
        self.assertFalse(at.exception, f"Streamlit app raised exception: {at.exception}")
        self.assertIsNotNone(at.session_state["audit_results"])
        self.assertGreater(len(at.session_state["audit_results"].risks), 0)

    def test_no_emojis_or_non_ascii_in_source_code(self):
        py_files = glob.glob("*.py")
        for filepath in py_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            non_ascii = [c for c in content if ord(c) > 127]
            self.assertEqual(len(non_ascii), 0, f"Non-ASCII characters found in {filepath}: {set(non_ascii)}")

if __name__ == "__main__":
    unittest.main()
