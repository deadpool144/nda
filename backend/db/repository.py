from sqlalchemy.orm import Session
from .models import ContractRecord

class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, contract_type: str, contract_json: dict, rule_based_contract: str) -> ContractRecord:
        db_contract = ContractRecord(
            user_id=user_id,
            contract_type=contract_type,
            contract_json=contract_json,
            rule_based_contract=rule_based_contract
        )
        self.db.add(db_contract)
        self.db.commit()
        self.db.refresh(db_contract)
        return db_contract

    def get(self, contract_id: int) -> ContractRecord:
        return self.db.query(ContractRecord).filter(ContractRecord.id == contract_id).first()

    def update_ai_enhancement(self, contract_id: int, ai_contract: str, user_prompt: str, validation_results: dict, metadata: dict):
        db_contract = self.get(contract_id)
        if db_contract:
            db_contract.ai_reformed_contract = ai_contract
            db_contract.user_ai_prompt = user_prompt
            db_contract.validation_results = validation_results
            db_contract.metadata_info = metadata
            self.db.commit()
            self.db.refresh(db_contract)
        return db_contract
        
    def update_docx_paths(self, contract_id: int, rule_path: str = None, ai_path: str = None):
        db_contract = self.get(contract_id)
        if db_contract:
            if rule_path:
                db_contract.rule_based_docx = rule_path
            if ai_path:
                db_contract.ai_reformed_docx = ai_path
            self.db.commit()
            self.db.refresh(db_contract)
        return db_contract
