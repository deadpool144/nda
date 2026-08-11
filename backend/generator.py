import re
from backend.database import db

def roman_numeral(n):
    val = [
        10, 9, 5, 4,
        1
        ]
    syb = [
        "x", "ix", "v", "iv",
        "i"
        ]
    roman_num = ''
    i = 0
    while  n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

def assemble_agreement(config):
    agreement_type = config.get("agreement_type", "NDA")
    is_mutual = config.get("nature", "Mutual") == "Mutual"
    industry = config.get("industry", "General Commercial")
    sub_sector = config.get("sub_sector", "")
    
    title = config.get("agreement_title", f"{agreement_type} Agreement").upper()
    effective_date = config.get("effective_date", "Date of Signing")
    if effective_date == "Date of Signing":
        effective_date_str = "[Date of Signing]"
    else:
        effective_date_str = config.get("custom_effective_date", "[Effective Date]")
        
    language = config.get("language", "English")
    
    # Parties
    parties = config.get("parties", [])
    num_parties = len(parties)
    
    # 1. Preamble
    preamble = f"THIS {title} (the \"Agreement\") is entered into on this {effective_date_str}\n\nBY AND BETWEEN:\n\n"
    party_blocks = []
    
    alphabet = "ABCDEFGHIJK"
    for idx, party in enumerate(parties):
        p_letter = alphabet[idx]
        name = party.get("name") or f"Party {p_letter}"
        e_type = party.get("entity_type") or "Company"
        reg = party.get("reg_number") or "[CIN/Registration Number]"
        gst = party.get("gst_number") or "[GST Number]"
        pan = party.get("pan_number") or "[PAN]"
        addr = party.get("address") or "[Registered Address]"
        email = party.get("email") or "[Email]"
        phone = party.get("phone") or "[Mobile Number]"
        
        sig_name = party.get("sig_name") or "[Authorized Signatory Name]"
        sig_desig = party.get("sig_designation") or "[Authorized Signatory Designation]"
        
        role = party.get("role") or f"Party {p_letter}"
        if is_mutual:
            role = f"Party {p_letter}"
        
        party_text = (
            f"{(name).upper()}, a {e_type} incorporated under applicable laws, with its registered office at {addr} "
            f"(CIN/Registration No: {reg}, GSTIN: {gst}, PAN: {pan}) (hereinafter referred to as the \"{role}\", "
            f"represented by its authorized signatory {sig_name}, {sig_desig}, which expression shall unless "
            f"repugnant to the context include its successors and permitted assigns)"
        )
        party_blocks.append(party_text)
        
    if num_parties == 2:
        preamble += party_blocks[0] + ";\n\nAND\n\n" + party_blocks[1] + "."
    else:
        preamble += ";\n\n".join(party_blocks[:-1]) + ";\n\nAND\n\n" + party_blocks[-1] + "."
        
    preamble += "\n\nEach is individually referred to as a \"Party\" and collectively as the \"Parties\"."
    if is_mutual:
        preamble += " Each Party may act as a Disclosing Party or Receiving Party under this Agreement."
    
    # 2. Recitals
    selected_purpose_name = config.get("selected_purpose", "")
    custom_purpose = config.get("custom_purpose", "")
    
    purpose_data = {}
    if selected_purpose_name:
        purpose_data = db.get_purposes().get(industry, {}).get(selected_purpose_name, {})
        
    recitals_list = []
    if purpose_data and purpose_data.get("recitals"):
        recitals_list = purpose_data["recitals"]
    elif custom_purpose:
        recitals_list = [
            f"WHEREAS, the Parties desire to discuss and evaluate commercial opportunities relating to: {custom_purpose};",
            "WHEREAS, in connection with such discussions, the Parties may disclose confidential and proprietary information to each other;",
            "WHEREAS, the Parties wish to protect such Confidential Information from unauthorized use, disclosure, or dissemination."
        ]
    else:
        recitals_list = [
            "WHEREAS, the Parties desire to evaluate and discuss a potential business relationship, transaction, or commercial opportunity;",
            "WHEREAS, in connection with such discussions, either Party may disclose certain confidential, proprietary, technical, commercial, or operational information to the other Party;",
            "WHEREAS, the Parties wish to establish the terms and conditions governing the disclosure, protection, use, and handling of such Confidential Information."
        ]
        
    recitals_text = "RECITALS\n\n" + "\n\n".join(recitals_list)
    recitals_text += "\n\nNOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, the Parties hereby agree as follows:"
    
    # 3. Definitions & Clauses
    nature_str = "Mutual" if is_mutual else "Unilateral"
    document_type = f"{nature_str} NDA"
    if selected_purpose_name:
        document_type = f"{nature_str} NDA - {industry} {selected_purpose_name} ({nature_str})"
        
    master_nda = db.get_master_nda_by_type(document_type)
    if not master_nda:
        master_nda = db.get_master_nda(is_mutual)
        
    if agreement_type != "NDA":
        return generate_other_agreement(agreement_type, preamble, recitals_text, config)
    
    # Generate Clauses First
    assembled_clauses = []
    clause_counter = 2
    
    clause_mapping = [
        ("2_EXCLUSIONS_FROM_CONFIDENTIAL_INFORMATION", "EXCLUSIONS FROM CONFIDENTIAL INFORMATION", False, ""),
        ("3_CONFIDENTIALITY_OBLIGATIONS", "CONFIDENTIALITY OBLIGATIONS", False, ""),
        ("4_PERMITTED_DISCLOSURES", "PERMITTED DISCLOSURES", False, ""),
        ("5_NON_USE_OBLIGATIONS", "NON-USE OBLIGATIONS", False, ""),
        ("6_COMPELLED_DISCLOSURE", "COMPELLED DISCLOSURE", False, ""),
        ("7_RETURN_OR_DESTRUCTION_OF_CONFIDENTIAL_INFORMATION", "RETURN OR DESTRUCTION OF CONFIDENTIAL INFORMATION", False, ""),
        ("8_INTELLECTUAL_PROPERTY_RIGHTS_AND_NO_LICENSE", "INTELLECTUAL PROPERTY RIGHTS AND NO LICENSE", False, ""),
        ("9_DATA_PROTECTION_AND_INFORMATION_SECURITY", "DATA PROTECTION AND INFORMATION SECURITY", True, "Data Protection"),
        ("10_NO_WARRANTY", "NO WARRANTY", False, ""),
        ("11_TERM_AND_TERMINATION", "TERM AND TERMINATION", False, ""),
        ("12_REMEDIES_AND_INJUNCTIVE_RELIEF", "REMEDIES AND INJUNCTIVE RELIEF", False, ""),
        ("13_LIMITATION_OF_LIABILITY", "LIMITATION OF LIABILITY", True, "Limitation of Liability"),
        ("14_INDEMNITY", "INDEMNITY", True, "Indemnity"),
        ("15_NON_CIRCUMVENTION_AND_NON_SOLICITATION", "NON-CIRCUMVENTION AND NON-SOLICITATION", True, "Non-Circumvention"),
        ("16_PUBLIC_ANNOUNCEMENTS", "PUBLIC ANNOUNCEMENTS", True, "Public Announcements"),
        ("17_MISCELLANEOUS", "MISCELLANEOUS", False, ""),
        ("18_GOVERNING_LAW", "GOVERNING LAW", False, ""),
        ("19_DISPUTE_RESOLUTION", "DISPUTE RESOLUTION", False, ""),
        ("20_NOTICES", "NOTICES", False, "")
    ]
    
    original_to_new_mapping = {}
    omitted_clauses = set()
    
    master_nda["17_MISCELLANEOUS"] = {
        "17.1": "Entire Agreement: This Agreement constitutes the entire agreement between the Parties relating to the subject matter hereof and supersedes all prior or contemporaneous agreements, understandings, and communications, whether written or oral.",
        "17.2": "Amendment: No modification, amendment, or waiver of any provision of this Agreement shall be effective unless in writing and signed by duly authorized representatives of both Parties.",
        "17.3": "Waiver: No failure or delay by either Party in exercising any right, power, or privilege hereunder shall operate as a waiver thereof, nor shall any single or partial exercise thereof preclude any other or further exercise thereof or the exercise of any other right, power, or privilege.",
        "17.4": "Severability: If any provision of this Agreement is held to be invalid, illegal, or unenforceable, the validity, legality, and enforceability of the remaining provisions shall not in any way be affected or impaired thereby.",
        "17.5": "Assignment: Neither Party may assign or transfer any of its rights or obligations under this Agreement without the prior written consent of the other Party, except that either Party may assign this Agreement to its successor in interest in connection with a merger, acquisition, or sale of all or substantially all of its assets.",
        "17.6": "Counterparts: This Agreement may be executed in counterparts, each of which shall be deemed an original, but all of which together shall constitute one and the same instrument.",
        "17.7": "Electronic Signatures: The Parties agree that this Agreement may be executed and delivered by electronic signature, which shall be deemed to have the same force and effect as a manual signature."
    }
    
    # Inject dynamic GOVERNING LAW
    dispute_config = config.get("dispute_resolution", {})
    gov_law = dispute_config.get("governing_law", "India")
    law_text = f"This Agreement shall be governed by and construed in accordance with the laws of {gov_law}."
    
    master_nda["18_GOVERNING_LAW"] = {
        "18.1": law_text
    }
    
    # Inject dynamic DISPUTE RESOLUTION
    mechanism = dispute_config.get("mechanism", "Arbitration")
    resolution_text = ""
    if mechanism == "Arbitration":
        inst = dispute_config.get("institution", "Ad Hoc Arbitration")
        seat = dispute_config.get("seat", "New Delhi")
        num_arbs = dispute_config.get("arbitrators", "Sole Arbitrator")
        lang = dispute_config.get("language", "English")
        pre_cond = dispute_config.get("pre_condition", "Direct Negotiation (30 Days)")
        
        pre_cond_clause = ""
        if pre_cond == "Direct Negotiation (30 Days)":
            pre_cond_clause = "The Parties shall attempt to resolve any dispute through direct negotiation for a period of thirty (30) days before initiating arbitration. "
        elif pre_cond == "Mediation then Arbitration":
            pre_cond_clause = "The Parties shall refer the dispute to mediation before commencing arbitration. "
            
        resolution_text = (
            f"Any dispute, controversy, or claim arising out of or relating to this Agreement shall be referred to and "
            f"finally resolved by arbitration. {pre_cond_clause}The arbitration shall be conducted under the rules of {inst}. "
        )
        if gov_law == "India":
            resolution_text += "The arbitration shall be governed by the Arbitration and Conciliation Act, 1996. "
        resolution_text += (
            f"The seat of arbitration shall be {seat}. The tribunal shall consist of a {num_arbs.lower()}. "
            f"The language of the arbitration shall be {lang}."
        )
    else:
        resolution_text = "Any dispute or claim arising out of or relating to this Agreement shall be subject to the exclusive jurisdiction of the competent courts of the arbitration seat or mutual jurisdiction."
        
    master_nda["19_DISPUTE_RESOLUTION"] = {
        "19.1": resolution_text
    }
    
    # Inject dynamic NOTICES
    notice_text = "Any notice or other communication under this Agreement shall be in writing and sent to the addresses listed below:"
    notice_clause = {"20.1": notice_text}
    
    for idx, party in enumerate(parties):
        p_letter = alphabet[idx]
        name = party.get("name") or f"Party {p_letter}"
        email = party.get("email") or "[Email]"
        addr = party.get("address") or "[Address]"
        attn = party.get("sig_name") or "[Authorized Signatory Name]"
        desig = party.get("sig_designation") or "[Designation]"
        notice_clause[f"20.{2+idx}"] = f"For {name}:\nAddress: {addr}\nEmail: {email}\nAttention: {attn} ({desig})"

    master_nda["20_NOTICES"] = notice_clause
    
    raw_clauses_text = ""
    
    for key, title_label, is_optional, opt_key in clause_mapping:
        original_num_match = re.match(r"^(\d+)_", key)
        orig_num = original_num_match.group(1) if original_num_match else None
        
        if is_optional:
            if key == "15_NON_CIRCUMVENTION_AND_NON_SOLICITATION":
                if "Non-Solicitation" not in config.get("optional_clauses", []) and "Non-Circumvention" not in config.get("optional_clauses", []):
                    if orig_num: omitted_clauses.add(orig_num)
                    continue
            elif opt_key not in config.get("optional_clauses", []):
                if orig_num: omitted_clauses.add(orig_num)
                continue
                
        clause_data = master_nda.get(key, {})
        if not clause_data:
            if orig_num: omitted_clauses.add(orig_num)
            continue
            
        if orig_num:
            original_to_new_mapping[orig_num] = str(clause_counter)
            
        def format_clause_text(data, is_clause_2_1=False, indent_level=0):
            if isinstance(data, str): return data.strip()
            if not isinstance(data, dict): return ""
                
            text_parts = []
            if "text" in data: text_parts.append(data["text"].strip())
            elif is_clause_2_1: text_parts.append("Notwithstanding anything contained in this Agreement, Confidential Information shall not include any information which the Receiving Party can demonstrate through written records:")
                
            sub_keys = [k for k in data.keys() if k != "text"]
            
            def sort_key(k):
                if k.isalpha() and len(k) == 1: return (0, k)
                return (1, k)
            sub_keys.sort(key=sort_key)
            
            items_str = []
            for i, k in enumerate(sub_keys):
                val = data[k]
                sub_text = format_clause_text(val, False, indent_level + 1)
                if sub_text:
                    if indent_level == 0:
                        prefix = chr(97 + i)
                        items_str.append(f"({prefix}) {sub_text.strip('; .')}")
                    elif indent_level == 1:
                        prefix = roman_numeral(i + 1)
                        items_str.append(f"({prefix}) {sub_text.strip('; .')}")
                    else:
                        items_str.append(sub_text.strip('; .'))
                        
            if items_str:
                indent = "    " * indent_level
                sub_indent = "    " * (indent_level + 1)
                
                for i in range(len(items_str)):
                    items_str[i] = re.sub(r'(?i)\s+or$', '', items_str[i])
                    items_str[i] = re.sub(r'(?i)\s+and$', '', items_str[i])
                    
                items_joined = f";\n{sub_indent}".join(items_str) + "."
                if text_parts: text_parts.append(f"\n{sub_indent}{items_joined}")
                else: text_parts.append(items_joined)
                
            if len(text_parts) > 1 and text_parts[1].startswith("\n"):
                return text_parts[0] + text_parts[1]
            return " ".join(text_parts)

        formatted_paras = []
        def sub_key_sort(k):
            try: return [int(x) for x in k.split('.') if x.isdigit()]
            except: return [k]
            
        sorted_sub_keys = sorted(clause_data.keys(), key=sub_key_sort)
        
        for idx, sub_key in enumerate(sorted_sub_keys):
            p_data = clause_data[sub_key]
            is_clause_2_1 = (key == "2_EXCLUSIONS_FROM_CONFIDENTIAL_INFORMATION" and "2.1" in sub_key)
            p = format_clause_text(p_data, is_clause_2_1)
            if not p: continue

            if "Restricted Period" in p or "two (2) years" in p:
                if "solicit" in p.lower():
                    sol_period = config.get("non_solicitation_period", "1 Year")
                    p = p.replace("two (2) years", sol_period.lower()).replace("Restricted Period", sol_period)
                if "circumvent" in p.lower():
                    circ_period = config.get("non_circumvention_period", "1 Year")
                    p = p.replace("two (2) years", circ_period.lower()).replace("Restricted Period", circ_period)
                    
            if "liability of either Party" in p and "INR [●]" in p:
                cap_choice = config.get("liability_cap", "No Cap")
                liab_num = original_to_new_mapping.get("13", "13")
                if cap_choice == "No Cap": p = f"Subject to Clause {liab_num}, neither Party shall exclude or limit its liability for direct damages arising out of its breach under this Agreement."
                else: p = p.replace("INR [●]", cap_choice)
                    
            if "data protection" in p.lower() or "personal data" in p.lower():
                dp_choice = config.get("data_protection_setting", "Basic")
                if dp_choice == "Enhanced": p += " The Parties shall implement enhanced encryption and ISO 27001 standards for information security."
                elif dp_choice == "DPDP Act, 2023": p += " Both Parties shall act as Data Fiduciaries and comply with the provisions of the Digital Personal Data Protection (DPDP) Act, 2023 of India."
                    
            if "three (3) years" in p or "thirty (30) days" in p or "survival period" in p.lower():
                if "Term" in title_label or "TERMINATION" in title_label:
                    term_val = config.get("agreement_term", "3 Years")
                    notice_val = config.get("notice_period", "30 Days")
                    p = p.replace("three (3) years", term_val.lower()).replace("thirty (30) days", notice_val.lower())
                    
            if "survival period" in p.lower() and "applicable" in p.lower() and not re.search(r"\d+\s*years", p):
                survival = config.get("survival_period", "five (5) years")
                p = p.replace("applicable survival period", f"survival period of {survival}")
                    
            prefix = f"{clause_counter}.{idx+1}"
            p = re.sub(r'^(\d+\.\d+)\s+', '', p)
            p = f"{prefix} {p}"
            formatted_paras.append(p)
                
        clause_body = "\n\n".join(formatted_paras)
        assembled_clauses.append(f"{clause_counter}. {title_label.upper()}\n\n{clause_body}")
        raw_clauses_text += f"\n\n{clause_body}"
        clause_counter += 1
        
    # Extract Capitalized Terms to auto-inject undefined terms
    found_terms = set(re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", raw_clauses_text))
    
    # Master dictionary to extract from
    master_defs_dict = {}
    if "1_DEFINITIONS" in master_nda and isinstance(master_nda["1_DEFINITIONS"], dict):
        for k, v in master_nda["1_DEFINITIONS"].items():
            if isinstance(v, dict) and "term" in v:
                master_defs_dict[v["term"]] = v.get("definition", "")
                
    # 1. Definitions
    def_dict = {}
    
    # Pre-fill standard ones to avoid missing
    standard_terms = ["Affiliate", "Agreement", "Applicable Law", "Confidential Information", "Purpose", "Representatives"]
    for p in parties:
        standard_terms.append(p.get("role", "Party"))
        
    for t in standard_terms:
        found_terms.add(t)
        
    for term in found_terms:
        # Avoid non-terms
        if term in ["The", "This", "Any", "All", "Each", "Subject", "Notwithstanding", "In", "Where", "If", "Party A", "Party B", "Party C"]: continue
        
        # Check if we should inject it
        def_text = ""
        
        # Is it in master NDA?
        if term in master_defs_dict:
            def_text = master_defs_dict[term]
        else:
            # Fallbacks
            if term == "Agreement": def_text = f'"Agreement" means this {title}, including all schedules, annexures, exhibits, amendments, and modifications.'
            elif term == "Purpose": 
                p_def = custom_purpose or "the evaluation, discussion, negotiation, assessment, and exploration of a potential business relationship."
                def_text = f'"Purpose" means {p_def}'
            elif term in [p.get("role") for p in parties]:
                def_text = f'"{term}" shall have the meaning ascribed to it in the Preamble of this Agreement.'
            elif term == "Trade Secret" and "Trade Secret" in config.get("optional_definitions", []):
                def_text = '"Trade Secret" means information that derives independent economic value from not being generally known and is subject to reasonable efforts to maintain its secrecy.'
            elif term == "Personal Data" and "Personal Data" in config.get("optional_definitions", []):
                def_text = '"Personal Data" means any information relating to an identified or identifiable natural person.'
            elif term == "Security Incident" and "Security Incident" in config.get("optional_definitions", []):
                def_text = '"Security Incident" means any unauthorized access, acquisition, use, disclosure, alteration, loss, or compromise of Confidential Information.'
            elif term == "Business Opportunity" and "Business Opportunity" in config.get("optional_definitions", []):
                def_text = '"Business Opportunity" means any actual, proposed, contemplated, or potential transaction, project, investment, acquisition, merger, joint venture, strategic alliance, or partnership.'
            elif term == "Business Day":
                gov_l = config.get("dispute_resolution", {}).get("governing_law", "India")
                def_text = f'"Business Day" means a day other than a Saturday, Sunday or public holiday in {gov_l}.'
                
        if def_text:
            if term == "Agreement":
                def_text = f'"Agreement" means this {title}, including all schedules, annexures, exhibits, amendments, modifications, and supplements hereto.'
            if term == "Purpose" and custom_purpose and not selected_purpose_name:
                def_text = f'"Purpose" means the evaluation, discussion, negotiation, assessment, and exploration of a potential business relationship relating to: "{custom_purpose}".'
            
            def_dict[term] = def_text

    # Include explicit optional definitions from config
    for opt_def in config.get("optional_definitions", []):
        if opt_def not in def_dict:
            if opt_def in master_defs_dict:
                def_dict[opt_def] = master_defs_dict[opt_def]
            elif opt_def == "Trade Secret":
                def_dict[opt_def] = '"Trade Secret" means information that derives independent economic value from not being generally known and is subject to reasonable efforts to maintain its secrecy.'
            elif opt_def == "Personal Data":
                def_dict[opt_def] = '"Personal Data" means any information relating to an identified or identifiable natural person.'
            elif opt_def == "Security Incident":
                def_dict[opt_def] = '"Security Incident" means any unauthorized access, acquisition, use, disclosure, alteration, loss, or compromise of Confidential Information.'
            elif opt_def == "Business Opportunity":
                def_dict[opt_def] = '"Business Opportunity" means any actual, proposed, contemplated, or potential transaction, project, investment, acquisition, merger, joint venture, strategic alliance, or partnership.'
            elif opt_def == "Business Day":
                gov_l = config.get("dispute_resolution", {}).get("governing_law", "India")
                def_dict[opt_def] = f'"Business Day" means a day other than a Saturday, Sunday or public holiday in {gov_l}.'

    def_lines = list(def_dict.values())
    def_lines.sort()
    
    definitions_clause = "1. DEFINITIONS\n\nFor the purposes of this Agreement, the following capitalized terms shall have the meanings assigned to them below:\n\n"
    definitions_clause += "\n\n".join([f"1.{idx+1} {line}" for idx, line in enumerate(def_lines)])
    
    # 5. Execution Block
    execution_text = (
        f"IN WITNESS WHEREOF, the Parties hereto have executed this {title} "
        f"as of the Effective Date written above.\n\n"
    )
    
    for idx, party in enumerate(parties):
        p_letter = alphabet[idx]
        name = party.get("name") or f"Party {p_letter}"
        sig_name = party.get("sig_name") or "[Signatory Name]"
        sig_desig = party.get("sig_designation") or "[Designation]"
        role = party.get("role") or f"Party {p_letter}"
        
        execution_text += (
            f"SIGNED AND DELIVERED for and on behalf of {name.upper()} ({role}):\n\n"
            f"___________________________________\n"
            f"Name: {sig_name}\n"
            f"Title: {sig_desig}\n\n"
        )
        if config.get("execution", {}).get("witness", "No") == "Yes":
            execution_text += (
                f"In the presence of Witness:\n"
                f"Name: _______________________\n"
                f"Address: _____________________\n\n"
            )
            
    assembled_clauses.append(execution_text.strip())
    
    full_body = "\n\n\n".join(assembled_clauses)
    
    # Replace broken clause references
    def replace_clause_ref(match):
        prefix = match.group(1) # 'Clause' or 'Clauses'
        orig_num = match.group(2)
        suffix = match.group(3) or ''
        if orig_num in original_to_new_mapping:
            return f"{prefix} {original_to_new_mapping[orig_num]}{suffix}"
        elif orig_num in omitted_clauses:
            return f"the relevant provisions (Omitted)"
        return match.group(0)
        
    full_body = re.sub(r"(Clause[s]?)\s+(\d+)(\.\d+)?", replace_clause_ref, full_body)
    
    if "Non-Circumvention" not in config.get("optional_clauses", []):
        full_body = full_body.replace("(g) Non-Circumvention and Non-Solicitation;", "(g) (Omitted);")
        full_body = full_body.replace(", Non-Circumvention and Non-Solicitation", "")
        full_body = full_body.replace("Non-Circumvention and Non-Solicitation,", "")
        
    full_body = re.sub(r';\s*or;', '; or', full_body)
    full_body = re.sub(r';\s*and;', '; and', full_body)
    
    # Final sweep for Placeholders
    # Skip Effective Date, Name, Designation, Title which are customized or meant for signature
    def replace_placeholder(match):
        val = match.group(1)
        if val in ["●", "Insert Jurisdiction", "Insert Number", "Insert Days", "Insert Address"]:
            return "________"
        return match.group(0)
        
    full_body = re.sub(r"\[(.*?)\]", replace_placeholder, full_body)

    full_document = f"{title}\n\n" + preamble + "\n\n" + recitals_text + "\n\n" + definitions_clause + "\n\n\n" + full_body
    return full_document

def generate_other_agreement(agreement_type, preamble, recitals, config):
    title = config.get("agreement_title", f"{agreement_type} Agreement").upper()
    parties = config.get("parties", [])
    optional_clauses = config.get("optional_clauses", [])
    
    clauses = [
        "1. SCOPE OF ENGAGEMENT\n\nThe Service Provider agrees to perform the services detailed in Schedule A (the \"Services\") in accordance with the terms of this Agreement, and the Client agrees to pay the fees set forth therein.",
        "2. FEES AND PAYMENT TERMS\n\nThe Client shall pay the Service Provider the fees within thirty (30) days of receipt of a valid tax invoice. Late payments shall bear interest at 1.5% per month.",
        "3. TERM AND TERMINATION\n\nThis Agreement shall commence on the Effective Date and remain in force for one (1) year. Either Party may terminate this Agreement for convenience by providing thirty (30) days' written notice.",
        "4. INTELLECTUAL PROPERTY\n\nAll intellectual property developed, created, or discovered in the course of performing the Services shall belong exclusively to the Client, subject to full payment of all fees due to the Service Provider.",
        "5. CONFIDENTIALITY\n\nEach Party shall maintain the confidentiality of all proprietary or confidential information received from the other Party and shall not disclose it to any third party except as required for the Purpose."
    ]
    
    c_idx = 6
    if "Limitation of Liability" in optional_clauses:
        cap = config.get("liability_cap", "No Cap")
        cap_str = f"limited to {cap}" if cap != "No Cap" else "uncapped"
        clauses.append(f"{c_idx}. LIMITATION OF LIABILITY\n\nThe total aggregate liability of either Party under this Agreement shall be {cap_str}, except in cases of fraud or wilful misconduct.")
        c_idx += 1
        
    if "Indemnity" in optional_clauses:
        clauses.append(f"{c_idx}. INDEMNIFICATION\n\nEach Party shall indemnify and hold harmless the other Party from any third-party claims arising from its gross negligence or breach of obligations under this Agreement.")
        c_idx += 1
        
    if "Data Protection" in optional_clauses:
        dp_setting = config.get("data_protection_setting", "Basic")
        clauses.append(f"{c_idx}. DATA PROTECTION\n\nThe Parties shall process personal data in accordance with all applicable data protection laws. Selection: {dp_setting} Compliance.")
        c_idx += 1
        
    dispute_config = config.get("dispute_resolution", {})
    gov_law = dispute_config.get("governing_law", "India")
    resolution_mechanism = dispute_config.get("mechanism", "Arbitration")
    
    resolution_text = ""
    if resolution_mechanism == "Arbitration":
        inst = dispute_config.get("institution", "Ad Hoc Arbitration")
        seat = dispute_config.get("seat", "New Delhi")
        resolution_text = f"resolved by arbitration under the rules of {inst} with the seat in {seat}."
    else:
        resolution_text = "subject to the exclusive jurisdiction of the competent courts."
        
    clauses.append(f"{c_idx}. GOVERNING LAW AND JURISDICTION\n\nThis Agreement is governed by the laws of {gov_law}. Any dispute shall be {resolution_text}")
    c_idx += 1
    
    notice_text = f"{c_idx}. NOTICE DETAILS\n\n"
    for idx, party in enumerate(parties):
        p_name = party.get("name") or f"Party {idx+1}"
        email = party.get("email") or "[Email]"
        notice_text += f"For {p_name}: Email: {email}\n"
    clauses.append(notice_text)
    c_idx += 1
    
    execution_text = f"IN WITNESS WHEREOF, the Parties hereto have executed this {title} as of the Effective Date.\n\n"
    for idx, party in enumerate(parties):
        name = party.get("name") or f"Party {idx+1}"
        sig_name = party.get("sig_name") or "[Signatory Name]"
        execution_text += f"SIGNED for and on behalf of {name.upper()}:\n\n___________________\nName: {sig_name}\n\n"
        
    clauses.append(execution_text)
    
    full_document = f"{title}\n\n" + preamble + "\n\n" + recitals + "\n\n" + "\n\n\n".join(clauses)
    return full_document
