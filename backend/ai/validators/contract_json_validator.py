from typing import Dict, Any, List
import re

class ContractJsonValidator:
    def __init__(self, contract_json: Dict[str, Any]):
        self.contract_json = contract_json
        
    def validate(self, ai_text: str, original_text: str = None) -> tuple[bool, List[str]]:
        errors = []
        
        def should_validate(field_value: str) -> bool:
            if not field_value:
                return False
            if original_text is not None:
                return field_value.upper() in original_text.upper()
            return True
        
        # 1. Validate Parties
        parties = self.contract_json.get("parties", [])
        for party in parties:
            name = party.get("name", "")
            if should_validate(name) and name.upper() not in ai_text.upper():
                errors.append(f"CRITICAL: Missing Party Name '{name}' in generated text.")
                
        # 2. Validate Governing Law
        dispute = self.contract_json.get("dispute_resolution", {})
        gov_law = dispute.get("governing_law", "")
        if should_validate(gov_law) and gov_law.upper() not in ai_text.upper():
            errors.append(f"CRITICAL: Missing Governing Law '{gov_law}' in generated text.")
            
        # 3. Validate Arbitration Seat
        seat = dispute.get("seat", "")
        if should_validate(seat) and dispute.get("mechanism") == "Arbitration" and seat.upper() not in ai_text.upper():
            errors.append(f"CRITICAL: Missing Arbitration Seat '{seat}' in generated text.")
            
        # 4. Validate Term
        term = self.contract_json.get("agreement_term", "")
        if should_validate(term) and "Year" in term and term.lower() not in ai_text.lower():
            num = re.search(r'\d+', term)
            if num and num.group(0) not in ai_text:
                errors.append(f"WARNING: Contract term number '{num.group(0)}' not found.")
        
        is_valid = len([e for e in errors if "CRITICAL" in e]) == 0
        return is_valid, errors
