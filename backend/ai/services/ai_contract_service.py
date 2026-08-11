from backend.db.session import SessionLocal
from backend.db.repository import ContractRepository
from backend.ai.pipeline.batch_generation_pipeline import BatchGenerationPipeline
from backend.ai.pipeline.comparison_pipeline import ComparisonPipeline
from backend.ai.schemas.contract_schema import EnhanceResponse
from typing import Dict, Any

class AIContractService:
    def __init__(self):
        self.batch_pipeline = BatchGenerationPipeline(batch_size=5, max_retries=2)
        self.comparison_pipeline = ComparisonPipeline()

    def enhance_contract(self, contract_type: str, contract_json: Dict[str, Any], rule_based_contract: str, user_prompt: str) -> EnhanceResponse:
        
        # 1. Save initial rule-based contract to DB (or assume it's done elsewhere and we just create a new record for tracking)
        db = SessionLocal()
        repo = ContractRepository(db)
        
        # Determine user ID (mocked as 1 for now)
        user_id = 1
        record = repo.create(
            user_id=user_id,
            contract_type=contract_type,
            contract_json=contract_json,
            rule_based_contract=rule_based_contract
        )
        
        # 2. Run AI Batch Enhancement Pipeline
        ai_reformed_text, ai_metadata = self.batch_pipeline.run(
            contract_json=contract_json,
            rule_based_contract=rule_based_contract,
            user_prompt=user_prompt,
            contract_type=contract_type
        )
        
        # 3. Run Comparison
        comparison_stats = self.comparison_pipeline.compare(rule_based_contract, ai_reformed_text)
        
        # 4. Update DB Record
        validation_results = {"status": "passed"} # Strict validation already done inside pipeline batch loop
        metadata = {
            "generation_metadata": ai_metadata,
            "comparison": comparison_stats
        }
        
        repo.update_ai_enhancement(
            contract_id=record.id,
            ai_contract=ai_reformed_text,
            user_prompt=user_prompt,
            validation_results=validation_results,
            metadata=metadata
        )
        db.close()
        
        return EnhanceResponse(
            status="success",
            ai_reformed_contract=ai_reformed_text,
            validation_results=validation_results,
            metadata=metadata
        )
