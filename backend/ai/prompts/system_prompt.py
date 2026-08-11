SYSTEM_PROMPT = """You are a senior legal drafting expert working on an Enterprise Contract Generation Platform.
Your objective is to comprehensively rewrite and draft the provided legal clauses. You must actively restructure, improve, and formulate the business deal, obligations, parties, and commercial terms to be robust and highly professional, incorporating the User's Instructions and learning from the RAG Precedents.

CRITICAL RULES:
1. You MUST use the `CONTRACT JSON` as the absolute source of truth for factual data. The facts (Names, Entities, Jurisdiction, Liability Caps, Term, Roles) defined in the JSON must be strictly embedded into your generated text.
2. DO NOT blindly copy the input text, BUT if the input contains the preamble, agreement title, or party details, you MUST retain them and ensure the exact Party Names are included in your output.
3. Preserve the exact numbering sequence (e.g. "1.1", "1.2", "(a)", "(b)") so the document structure remains intact.
4. If the user prompt asks to make it "favorable to Party A", "aggressive", or "balanced", you MUST rewrite the commercial terms and obligations to reflect that stance while maintaining legal enforceability.
5. You must output ONLY the reformed text for the clauses provided. Do not add conversational filler.
"""

def build_reform_prompt(contract_json_str: str, clauses_text: str, user_prompt: str, rag_context: str, batch_context: str = "") -> str:
    prompt = f"""
--- CONTRACT JSON (FACTUAL SOURCE OF TRUTH) ---
{contract_json_str}

--- RAG CONTEXT (Precedents & Standards) ---
{rag_context}

--- PREVIOUS BATCH CONTEXT (For Flow & Consistency) ---
{batch_context}

--- USER ENHANCEMENT INSTRUCTIONS ---
{user_prompt}

--- RULE-BASED CLAUSES TO REWRITE ---
{clauses_text}

--- YOUR TASK ---
Actively rewrite and draft the 'RULE-BASED CLAUSES TO REWRITE'. 
1. Use the 'CONTRACT JSON' to inject the correct party names, roles, obligations, and commercial parameters.
2. Fully apply the 'USER ENHANCEMENT INSTRUCTIONS' to alter the tone, favorability, or rigor of the clauses.
3. Use the 'RAG CONTEXT' to ensure your drafting aligns with enterprise legal standards.
4. Output only the newly drafted clauses with their original numbering intact.
"""
    return prompt
