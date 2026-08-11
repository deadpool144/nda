from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ContractSchema(BaseModel):
    contract_json: Dict[str, Any]
    rule_based_contract: str
    user_prompt: str

class EnhanceRequest(BaseModel):
    contract_type: str
    contract_json: Dict[str, Any]
    rule_based_contract: str
    user_prompt: str

class EnhanceResponse(BaseModel):
    status: str
    ai_reformed_contract: str
    validation_results: Dict[str, Any]
    metadata: Dict[str, Any]

class BatchResponse(BaseModel):
    reformed_clauses: str

class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str]
