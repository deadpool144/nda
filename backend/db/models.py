from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
from .session import Base

class ContractRecord(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)
    contract_type = Column(String, index=True)
    contract_json = Column(JSON, nullable=False)
    rule_based_contract = Column(Text, nullable=False)
    rule_based_docx = Column(String, nullable=True) # Path to file
    ai_reformed_contract = Column(Text, nullable=True)
    ai_reformed_docx = Column(String, nullable=True) # Path to file
    user_ai_prompt = Column(Text, nullable=True)
    validation_results = Column(JSON, nullable=True)
    metadata_info = Column(JSON, nullable=True) # For retry attempts, token usage etc
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
