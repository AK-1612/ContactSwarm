import os
import shutil
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pypdf import PdfReader
from orchestrator import run_contract_swarm, run_vdr_zip_audit
from state import VDRAnalysisState

app = FastAPI(
    title="ContractSwarm Multi-Agent VDR Fabric",
    description="Autonomous M&A contract risk analysis engine.",
    version="2.0.0"
)

class AnalysisRequest(BaseModel):
    pdf_path: str = Field(description="Path to local contract file or PDF")

class ZipAnalysisRequest(BaseModel):
    zip_path: str = Field(description="Path to local ZIP file containing corporate contracts")

@app.post("/analyze-contract")
def analyze_contract(request: AnalysisRequest):
    if not os.path.exists(request.pdf_path):
        raise HTTPException(status_code=404, detail=f"Contract PDF path not found: {request.pdf_path}")
    
    try:
        reader = PdfReader(request.pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        doc_name = os.path.basename(request.pdf_path)
        initial_state = VDRAnalysisState(
            vdr_package_name=doc_name,
            contracts={doc_name: text},
            contract_text=text,
            risks=[],
            executive_summary=""
        )
        final_state = run_contract_swarm(initial_state)
        
        return {
            "status": "success",
            "executive_summary": final_state.executive_summary,
            "portfolio_metrics": final_state.portfolio_metrics,
            "risk_matrix": [r.model_dump() for r in final_state.risks]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-vdr-zip")
def analyze_vdr_zip(request: ZipAnalysisRequest):
    if not os.path.exists(request.zip_path):
        raise HTTPException(status_code=404, detail=f"VDR ZIP package not found: {request.zip_path}")
    
    try:
        final_state = run_vdr_zip_audit(request.zip_path, package_name=os.path.basename(request.zip_path))
        return {
            "status": "success",
            "vdr_package": final_state.vdr_package_name,
            "executive_summary": final_state.executive_summary,
            "portfolio_metrics": final_state.portfolio_metrics,
            "risk_matrix": [r.model_dump() for r in final_state.risks]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-vdr-zip")
async def upload_vdr_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported for VDR batch upload.")
        
    try:
        content = await file.read()
        final_state = run_vdr_zip_audit(content, package_name=file.filename)
        return {
            "status": "success",
            "vdr_package": final_state.vdr_package_name,
            "executive_summary": final_state.executive_summary,
            "portfolio_metrics": final_state.portfolio_metrics,
            "risk_matrix": [r.model_dump() for r in final_state.risks]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
