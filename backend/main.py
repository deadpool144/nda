import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List

# Define BASE_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Force UTF-8 standard output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

from backend.database import db
from backend.generator import assemble_agreement
from backend.exporter import export_to_docx
from backend.db.session import engine, Base
from backend.ai.schemas.contract_schema import EnhanceRequest
from backend.ai.services.ai_contract_service import AIContractService

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LexForge Contract Creator Platform",
    description="Interactive Contract Form Wizard and Exporter",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    agreement_type: str
    nature: str
    agreement_title: str
    effective_date: str
    custom_effective_date: str = ""
    language: str
    industry: str
    sub_sector: str = ""
    parties: List[Dict[str, Any]]
    selected_purpose: str = ""
    custom_purpose: str = ""
    agreement_term: str
    notice_period: str
    renewal: str
    optional_clauses: List[str]
    optional_definitions: List[str]
    liability_cap: str = "No Cap"
    non_solicitation_period: str = "1 Year"
    non_circumvention_period: str = "1 Year"
    data_protection_setting: str = "Basic"
    dispute_resolution: Dict[str, Any]
    execution: Dict[str, Any]

class ExportRequest(BaseModel):
    title: str
    text: str

class RiskRequest(BaseModel):
    text: str

@app.get("/api/purposes")
async def get_purposes():
    return db.get_purposes()

@app.get("/api/master-schema")
async def get_master_schema(mutual: bool = True):
    return db.mutual_master if mutual else db.unilateral_master

@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    try:
        doc_text = assemble_agreement(req.model_dump())
        return {"status": "success", "contract_text": doc_text}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/export/docx")
async def api_export_docx(req: ExportRequest):
    try:
        stream = export_to_docx(req.title, req.text)
        filename = f"{req.title.replace(' ', '_').lower()}.docx"
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/enhance")
async def api_enhance_contract(req: EnhanceRequest):
    try:
        service = AIContractService()
        response = service.enhance_contract(
            contract_type=req.contract_type,
            contract_json=req.contract_json,
            rule_based_contract=req.rule_based_contract,
            user_prompt=req.user_prompt
        )
        return response.model_dump()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, detail=str(e))

@app.post("/api/risk-review")
async def api_risk_review(req: RiskRequest):
    text = req.text
    # We can analyze the text for risk markers and return simulated AI Risk reviews
    risks = []
    
    # Analyze text for common warnings
    if "No Cap" in text or "uncapped" in text or "[●]" in text or "INR [●]" in text:
        risks.append({
            "severity": "Critical",
            "clause": "Limitation of Liability",
            "issue": "Liability is uncapped or contains unfilled placeholders.",
            "suggestion": "Specify a liability cap (e.g. 50% or 100% of fees paid) to avoid unlimited financial exposure."
        })
        
    if "Governing Law: India" in text and "direct negotiation" not in text.lower() and "mediation" not in text.lower():
        risks.append({
            "severity": "Medium",
            "clause": "Dispute Resolution",
            "issue": "No pre-arbitration mediation or negotiation conditions are set.",
            "suggestion": "Add a 30-day direct negotiation or mediation requirement before initiating costly arbitration."
        })
        
    if "Non-Solicitation" in text and "3 Years" in text:
        risks.append({
            "severity": "High",
            "clause": "Non-Solicitation",
            "issue": "The 3-year restricted period is exceptionally long.",
            "suggestion": "Reduce the restricted period to 1 or 2 years to improve enforceability under local labor laws."
        })
        
    if "personal data" in text.lower() and "DPDP Act, 2023" not in text:
        risks.append({
            "severity": "Low",
            "clause": "Data Protection",
            "issue": "General data protection compliance is set but does not explicitly reference the Indian DPDP Act, 2023.",
            "suggestion": "If operating in India, upgrade to DPDP Act, 2023 compliance to ensure legal alignment."
        })
        
    if not risks:
        risks.append({
            "severity": "Low",
            "clause": "General Audit",
            "issue": "No immediate critical risks detected based on configuration.",
            "suggestion": "Ensure all party signatures and dates are collected properly."
        })
        
    return {"status": "success", "risks": risks}

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"status": "success", "message": "LexForge API is running. Frontend static directory not found."}
