# Week 24: ContractSwarm - Multi-Agent M&A Due Diligence Fabric

## 1. Executive Summary

ContractSwarm is an autonomous multi-agent fabric designed to accelerate Virtual Data Room (VDR) contract reviews during M&A due diligence. It deploys specialized cognitive agents (Legal, Financial, and Human Capital) orchestrated via a LangGraph state graph to audit unstructured corporate contracts, index liabilities using FAISS vector indexing, and output a unified JSON risk matrix and executive summary tailored for M&A partners.

---

## 2. Realization and Implementation Status

### Objective Realization Matrix

| Requirement / Pillar | Specified Requirement | Realization Status | Implementation Evidence |
| :--- | :--- | :--- | :--- |
| **Focus** | Autonomous Virtual Data Room (VDR) Analysis | Fully Realized (100%) | Autonomous extraction and auditing of entire multi-contract VDR packages. |
| **Objective** | Orchestrate specialized swarm (Legal, Financial, HR) | Fully Realized (100%) | Multi-agent swarm deployed in `orchestrator.py` with domain-specific agents in `legal_agent.py`, `financial_agent.py`, `hr_agent.py`. |
| **Tech: Python** | Python 3.12 runtime environment | Fully Realized (100%) | Clean Python 3.12 codebase, type annotations, and virtual environment setup. |
| **Tech: LangGraph** | Multi-agent state orchestration | Fully Realized (100%) | `StateGraph` DAG pipeline in `orchestrator.py` executing indexing, agent swarms, and executive synthesis. |
| **Tech: Azure Doc Intel** | Contract parsing engine | Fully Realized (100%) | Hybrid parser in `doc_parser.py`: Azure Document Intelligence API adapter with zero-credential offline fallback via PyPDF. |
| **Tech: FAISS** | Semantic clause vector indexing | Fully Realized (100%) | `FAISSContractIndexer` in `faiss_indexer.py`: dense embedding generation, clause indexing, and semantic similarity search. |
| **Tech: Pydantic** | Type-safe state & schema enforcement | Fully Realized (100%) | Pydantic v2 models in `state.py` (`RiskItem`, `VDRAnalysisState`) and FastAPI request validation. |
| **Key Deliverable** | Ingest ZIP file of contracts, output unified JSON risk matrix and partner executive summary | Fully Realized (100%) | Implemented via `run_vdr_zip_audit()`, FastAPI `/analyze-vdr-zip`, and the Streamlit VDR ZIP ingestion interface. |
| **Executive Interface** | EY-grade M&A Diligence Dashboard | Fully Realized (100%) | Streamlit UI in `app.py` adhering to EY corporate identity (no emojis, no symbols, pure typography). |

---

## 3. Technology Stack Alignment

1. **Python 3.12**: Modern asynchronous and synchronous execution runtime.
2. **LangGraph StateGraph Engine**: Graph-based execution graph coordinating document intake, FAISS indexing, specialized agent swarms, and partner memorandum synthesis.
3. **Azure Document Intelligence & Local Fallback Engine**: Configurable OCR and layout extraction adapter (`doc_parser.py`) supporting both cloud Azure Document Intelligence endpoints and deterministic local PyPDF extraction.
4. **FAISS Vector Store (`faiss-cpu`)**: High-performance in-memory vector database indexing segmented contract clauses and enabling semantic similarity search across VDR portfolios.
5. **Pydantic v2**: Strict schema definition and validation for risk items, severity classifications, mitigation strategies, and state transfers.
6. **Streamlit (EY Institutional Design)**: Partner-grade due diligence dashboard with zero emojis and zero decorative symbols, featuring portfolio KPI counters, interactive risk matrix filtering, and audit memo generation.
7. **FastAPI & Uvicorn**: High-throughput REST API supporting batch ZIP uploads and single contract analysis.

---

## 4. Multi-Agent Swarm Architecture

The pipeline executes a directed acyclic graph (DAG) across five nodes:

1. **Node 1: VDR Ingestion & FAISS Vector Indexing (`index_vdr`)**
   - Unpacks the VDR ZIP archive and extracts all corporate contracts (PDF, TXT, MD).
   - Segments contract text into structural clauses.
   - Generates normalized dense embedding vectors and populates the FAISS inner-product index.

2. **Node 2: Legal Workstream Agent (`legal_agent`)**
   - Queries FAISS for legal liability clauses.
   - Flags indemnification obligations, uncapped liabilities, change of control restrictions, and exclusivity/MFN covenants.
   - Prescribes contractual mitigation strategies and liability caps.

3. **Node 3: Financial Workstream Agent (`financial_agent`)**
   - Queries FAISS for financial commitments and treasury impacts.
   - Flags liquidated damages, compounding default penalties, minimum commitments/take-or-pay clauses, and extended payment terms (Net 90/120).

4. **Node 4: Human Capital Workstream Agent (`hr_agent`)**
   - Queries FAISS for key personnel liabilities.
   - Flags executive golden parachute severance, single-trigger equity acceleration, key person operational dependencies, and non-compete covenants.

5. **Node 5: M&A Partner Synthesizer (`partner_synthesizer`)**
   - Consolidates all agent findings into a unified risk matrix.
   - Calculates portfolio metrics: contract breakdown, severity counts, and overall transaction risk profile (ELEVATED, MODERATE, LOW).
   - Generates the executive diligence summary suitable for M&A partners.

---

## 5. Key Deliverables & Output Formats

### Ingestion

Ingests a `.zip` archive containing multiple target corporate agreements (e.g., `vdr_docs/VDR_Corporate_Contracts_Package.zip`).

### Unified JSON Risk Matrix

```json
{
  "engagement": "Project Horizon Due Diligence",
  "vdr_package": "VDR_Corporate_Contracts_Package.zip",
  "status": "ACTION REQUIRED",
  "executive_summary": "M&A Due Diligence Executive Summary: Portfolio review of 3 VDR contract(s) completed with ELEVATED risk profile. Total Liabilities Flagged: 17 (High Severity: 9, Medium Severity: 7, Low Severity: 1)...",
  "portfolio_metrics": {
    "total_contracts_audited": 3,
    "total_liabilities_flagged": 17,
    "high_severity_count": 9,
    "medium_severity_count": 7,
    "low_severity_count": 1,
    "overall_portfolio_risk": "ELEVATED",
    "contract_breakdown": {
      "Project_Horizon_Merger_Agreement.pdf": 7,
      "Vendor_Master_Services_Agreement.pdf": 6,
      "Executive_Retention_Agreement.pdf": 4
    }
  },
  "risk_matrix": [
    {
      "contract_name": "Project_Horizon_Merger_Agreement.pdf",
      "category": "Legal",
      "severity": "High",
      "clause_reference": "Indemnification / Liability Clause",
      "description": "Broad indemnification obligations detected; potential open-ended liability post-acquisition.",
      "mitigation": "Negotiate a bilateral liability cap tied to 10-15% of contract value and exclude consequential damages."
    }
  ]
}
```

---

## 6. Quickstart Guide

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Generate Sample VDR Documents & ZIP Archive

```bash
python generate_samples.py
```

Generates sample PDF agreements and packages them into `vdr_docs/VDR_Corporate_Contracts_Package.zip`.

### 3. Launch Streamlit Executive UI

```bash
streamlit run app.py
```

Access the partner dashboard at `http://localhost:8501`.

### 4. Launch REST API Server

```bash
uvicorn server:app --reload --port 8000
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- Endpoints:
  - `POST /analyze-vdr-zip`: Analyzes a local VDR ZIP file.
  - `POST /upload-vdr-zip`: Accepts multipart/form-data ZIP file upload.
  - `POST /analyze-contract`: Analyzes an individual contract file.

### 5. Execute Test Suite

```bash
python test_pipeline.py
```

All 7 integration and unit tests execute in under 0.5s with zero exceptions.
