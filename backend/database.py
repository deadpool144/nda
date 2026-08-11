import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DICT_DIR = os.path.join(os.path.dirname(BASE_DIR), "dictionary")

def load_json_file(path_parts):
    path = os.path.join(*path_parts)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

class ContractDatabase:
    def __init__(self):
        self.mutual_master = load_json_file([DATA_DIR, "mutual_nda_structured.json"])
        self.unilateral_master = load_json_file([DATA_DIR, "unilateral_nda_structured.json"])
        self.nda_purposes = load_json_file([DATA_DIR, "nda_purposes.json"])
        self.all_grouped = load_json_file([DICT_DIR, "all_grouped.json"])
        
    def get_purposes(self, industry=None):
        """Returns list of purposes and details grouped by industry."""
        if industry:
            return self.nda_purposes.get(industry, {})
        return self.nda_purposes

    def get_master_nda(self, is_mutual=True):
        return self.mutual_master if is_mutual else self.unilateral_master
        
    def get_master_nda_by_type(self, document_type):
        """Builds a complete master NDA structure for a specific document type dynamically."""
        if not self.all_grouped:
            return None
            
        master_nda = {}
        for clause_key, docs in self.all_grouped.items():
            doc_data = next((d for d in docs if d['document_type'] == document_type), None)
            if doc_data:
                master_nda[clause_key] = doc_data['clauses']
                
        if not master_nda:
            return None
            
        return master_nda

db = ContractDatabase()
