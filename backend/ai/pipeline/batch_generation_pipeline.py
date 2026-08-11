import json
import re
import time
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from backend.ai.models.provider import get_generation_llm
from backend.ai.rag.retriever import ContractRetriever
from backend.ai.prompts.system_prompt import SYSTEM_PROMPT, build_reform_prompt
from backend.ai.validators.contract_json_validator import ContractJsonValidator

class BatchGenerationPipeline:
    def __init__(self, batch_size: int = 5, max_retries: int = 2):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.llm = get_generation_llm()
        self.retriever = ContractRetriever()
        
    def _split_into_clauses(self, full_text: str) -> List[str]:
        # Split by numbered headings e.g. "1. DEFINITIONS", "2. OBLIGATIONS"
        # We look for \n\n\d+\. [A-Z ]+\n
        # Prepend a dummy newline for the first match
        text = "\n\n" + full_text.strip()
        parts = re.split(r'\n\n(?=\d+\.\s+[A-Z])', text)
        return [p.strip() for p in parts if p.strip()]

    def run(self, contract_json: Dict[str, Any], rule_based_contract: str, user_prompt: str, contract_type: str) -> tuple[str, dict]:
        clauses = self._split_into_clauses(rule_based_contract)
        
        # If splitting failed or document is tiny, treat as 1 batch
        if not clauses:
            clauses = [rule_based_contract]
            
        batches = [clauses[i:i + self.batch_size] for i in range(0, len(clauses), self.batch_size)]
        
        reformed_clauses = []
        metadata = {"batches_processed": len(batches), "retries": 0}
        
        json_str = json.dumps(contract_json, indent=2)
        validator = ContractJsonValidator(contract_json)
        
        previous_batch_context = "No previous context. This is the start of the contract."
        
        for batch_idx, batch in enumerate(batches):
            batch_text = "\n\n".join(batch)
            
            # Retrieve RAG context based on the batch's text concepts
            rag_docs = self.retriever.retrieve(query=batch_text[:1000], contract_type=contract_type, k=4)
            rag_context = "\n\n".join([d.page_content for d in rag_docs]) if rag_docs else "No specific context found."
            
            prompt_str = build_reform_prompt(
                contract_json_str=json_str,
                clauses_text=batch_text,
                user_prompt=user_prompt,
                rag_context=rag_context,
                batch_context=previous_batch_context
            )
            
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt_str)
            ]
            
            # Retry logic
            attempt = 0
            success = False
            reformed_text = ""
            
            while attempt <= self.max_retries and not success:
                try:
                    response = self.llm.invoke(messages)
                    content = response.content
                    if isinstance(content, list):
                        reformed_text = "".join([
                            part.get("text", "") if isinstance(part, dict) else (part.text if hasattr(part, 'text') else str(part)) 
                            for part in content
                        ]).strip()
                    else:
                        reformed_text = str(content).strip()
                    
                    # Validate output against json strictly (only for fields present in original text)
                    is_valid, errors = validator.validate(reformed_text, original_text=batch_text)
                    if is_valid:
                        success = True
                    else:
                        print(f"Validation failed on batch {batch_idx}, attempt {attempt}: {errors}")
                        attempt += 1
                        metadata["retries"] += 1
                        # Append the failure feedback to the LLM to self-correct
                        messages.append(SystemMessage(content=f"Your previous attempt failed validation: {', '.join(errors)}. Please correct this and strictly adhere to the Contract JSON."))
                        time.sleep(2) # Backoff
                        
                except Exception as e:
                    print(f"LLM Exception on batch {batch_idx}: {e}")
                    attempt += 1
                    metadata["retries"] += 1
                    time.sleep(2)
            
            if not success:
                # Fallback to original text if AI fails to generate valid text after retries
                print(f"Batch {batch_idx} failed after {self.max_retries} retries. Falling back to rule-based.")
                reformed_text = batch_text
                
            reformed_clauses.append(reformed_text)
            
            # Update context for next batch (last 500 chars to maintain flow)
            previous_batch_context = reformed_text[-500:] if len(reformed_text) > 500 else reformed_text

        final_contract = "\n\n".join(reformed_clauses)
        return final_contract, metadata
