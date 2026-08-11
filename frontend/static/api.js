// api.js — Contract Creator Logic

let currentStep = 1;
const totalSteps = 16;
let purposeDatabase = {};
let isEditingDirectly = false;
let manualContractText = "";

// Initial State
const state = {
    agreement_type: "NDA",
    nature: "Mutual",
    agreement_title: "MUTUAL NON-DISCLOSURE AGREEMENT",
    effective_date: "Date of Signing",
    custom_effective_date: "",
    language: "English",
    industry: "General Commercial",
    sub_sector: "",
    parties: [
        {
            name: "Alpha Corp",
            entity_type: "Private Limited Company",
            reg_number: "U72200DL2023PTC123456",
            gst_number: "07AAAAA1111A1Z1",
            pan_number: "AAAAA1111A",
            address: "101 Cyber Tower, Nehru Place, New Delhi 110019",
            email: "legal@alphacorp.com",
            phone: "+91-9876543210",
            sig_name: "John Doe",
            sig_designation: "Director",
            role: "Disclosing Party & Receiving Party"
        },
        {
            name: "Beta Solutions",
            entity_type: "Partnership Firm",
            reg_number: "REG-987654321",
            gst_number: "27BBBBB2222B2Z2",
            pan_number: "BBBBB2222B",
            address: "502 Tech Park, Bandra West, Mumbai 400050",
            email: "ops@betasolutions.com",
            phone: "+91-9123456789",
            sig_name: "Jane Smith",
            sig_designation: "Managing Partner",
            role: "Disclosing Party & Receiving Party"
        }
    ],
    selected_purpose: "",
    custom_purpose: "",
    agreement_term: "3 Years",
    notice_period: "30 Days",
    renewal: "Auto Renewal",
    optional_clauses: ["Data Protection", "Limitation of Liability", "Indemnity", "Force Majeure", "Non-Solicitation", "Non-Circumvention", "Public Announcements"],
    optional_definitions: ["Affiliate", "Trade Secret", "Personal Data", "Security Incident", "Business Opportunity", "Introduced Contact", "Restricted Personnel"],
    liability_cap: "No Cap",
    non_solicitation_period: "1 Year",
    non_circumvention_period: "1 Year",
    data_protection_setting: "Basic",
    dispute_resolution: {
        governing_law: "India",
        state: "Delhi",
        mechanism: "Arbitration",
        institution: "Ad Hoc Arbitration",
        seat: "New Delhi",
        arbitrators: "Sole Arbitrator",
        language: "English",
        pre_condition: "Direct Negotiation (30 Days)"
    },
    execution: {
        signatures: "Yes",
        counterparts: "Yes",
        witness: "No"
    }
};

document.addEventListener("DOMContentLoaded", () => {
    initApp();
    loadPurposes();
    loadMasterSchema().then(() => {
        setupEventListeners();
        renderPartiesForms();
        renderRoleIdentification();
        toggleClauseConfigPanels();
        triggerLivePreview();
    });
});

function initApp() {
    // Light/Dark Theme toggle
    const toggle = document.getElementById("theme-toggle");
    if (toggle) {
        toggle.addEventListener("click", () => {
            document.body.classList.toggle("light-theme");
        });
    }
}

function loadPurposes() {
    fetch("/api/purposes")
        .then(res => res.json())
        .then(data => {
            purposeDatabase = data;
            populatePurposesDropdown();
        })
        .catch(err => console.error("Error loading purposes:", err));
}

function populatePurposesDropdown() {
    const select = document.getElementById("purpose-template-select");
    select.innerHTML = '<option value="">-- Choose Purpose --</option>';
    
    const ind = state.industry;
    const list = purposeDatabase[ind] || {};
    
    Object.keys(list).forEach(pName => {
        const opt = document.createElement("option");
        opt.value = pName;
        opt.textContent = pName;
        select.appendChild(opt);
    });
    
    // If selected_purpose is set, select it
    if (state.selected_purpose && list[state.selected_purpose]) {
        select.value = state.selected_purpose;
    }
}

function renderPartiesForms() {
    const container = document.getElementById("parties-cards-container");
    container.innerHTML = "";
    
    state.parties.forEach((party, idx) => {
        const card = document.createElement("div");
        card.className = "party-config-card";
        
        const partyLetter = String.fromCharCode(65 + idx);
        card.innerHTML = `
            <h3>Party ${partyLetter} Details</h3>
            <div class="party-fields-grid">
                <div class="form-group">
                    <label>Entity Name</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="name" value="${party.name || ""}">
                </div>
                <div class="form-group">
                    <label>Entity Type</label>
                    <select class="form-control party-input" data-index="${idx}" data-field="entity_type">
                        <option value="Private Limited Company" ${party.entity_type === "Private Limited Company" ? "selected" : ""}>Private Limited Company</option>
                        <option value="Public Limited Company" ${party.entity_type === "Public Limited Company" ? "selected" : ""}>Public Limited Company</option>
                        <option value="LLP" ${party.entity_type === "LLP" ? "selected" : ""}>LLP</option>
                        <option value="Partnership Firm" ${party.entity_type === "Partnership Firm" ? "selected" : ""}>Partnership Firm</option>
                        <option value="Proprietorship" ${party.entity_type === "Proprietorship" ? "selected" : ""}>Proprietorship</option>
                        <option value="Individual" ${party.entity_type === "Individual" ? "selected" : ""}>Individual</option>
                        <option value="Trust" ${party.entity_type === "Trust" ? "selected" : ""}>Trust</option>
                        <option value="Government Entity" ${party.entity_type === "Government Entity" ? "selected" : ""}>Government Entity</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>CIN / Reg Number</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="reg_number" value="${party.reg_number || ""}">
                </div>
                <div class="form-group">
                    <label>GSTIN</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="gst_number" value="${party.gst_number || ""}">
                </div>
                <div class="form-group">
                    <label>PAN</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="pan_number" value="${party.pan_number || ""}">
                </div>
                <div class="form-group">
                    <label>Mobile Number</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="phone" value="${party.phone || ""}">
                </div>
                <div class="form-group full-width">
                    <label>Registered Address</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="address" value="${party.address || ""}">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="email" value="${party.email || ""}">
                </div>
                <div class="form-group">
                    <label>Authorized Signatory Name</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="sig_name" value="${party.sig_name || ""}">
                </div>
                <div class="form-group">
                    <label>Signatory Designation</label>
                    <input type="text" class="form-control party-input" data-index="${idx}" data-field="sig_designation" value="${party.sig_designation || ""}">
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    // Wire up listeners for party inputs
    document.querySelectorAll(".party-input").forEach(el => {
        el.addEventListener("input", (e) => {
            const idx = parseInt(e.target.dataset.index);
            const field = e.target.dataset.field;
            state.parties[idx][field] = e.target.value;
            triggerLivePreview();
        });
    });
    
    renderNoticeDetailsForms();
}

function renderNoticeDetailsForms() {
    const container = document.getElementById("notice-details-container");
    container.innerHTML = "";
    
    state.parties.forEach((party, idx) => {
        const partyLetter = String.fromCharCode(65 + idx);
        const card = document.createElement("div");
        card.className = "party-config-card";
        card.innerHTML = `
            <h3>Party ${partyLetter} Notices</h3>
            <div class="party-fields-grid">
                <div class="form-group full-width">
                    <label>Notice Address</label>
                    <input type="text" class="form-control notice-input" data-index="${idx}" data-field="address" value="${party.address || ""}">
                </div>
                <div class="form-group">
                    <label>Notice Email</label>
                    <input type="text" class="form-control notice-input" data-index="${idx}" data-field="email" value="${party.email || ""}">
                </div>
                <div class="form-group">
                    <label>Attention To</label>
                    <input type="text" class="form-control notice-input" data-index="${idx}" data-field="sig_name" value="${party.sig_name || ""}">
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    document.querySelectorAll(".notice-input").forEach(el => {
        el.addEventListener("input", (e) => {
            const idx = parseInt(e.target.dataset.index);
            const field = e.target.dataset.field;
            state.parties[idx][field] = e.target.value;
            triggerLivePreview();
        });
    });
}

function updatePartyRoles() {
    const isMutual = state.nature === "Mutual";
    const type = state.agreement_type;
    
    if (type !== "NDA") {
        let role1 = "Contractor";
        let role2 = "Employer";
        if (type === "Service Agreement") { role1 = "Service Provider"; role2 = "Client"; }
        else if (type === "Consultancy Agreement") { role1 = "Consultant"; role2 = "Client"; }
        else if (type === "Vendor Agreement") { role1 = "Vendor"; role2 = "Purchaser"; }
        else if (type === "Supply Agreement") { role1 = "Supplier"; role2 = "Purchaser"; }
        else if (type === "Power Purchase Agreement") { role1 = "Power Seller"; role2 = "Power Purchaser"; }
        
        state.parties[0].role = role1;
        state.parties[1].role = role2;
        if (state.parties[2]) state.parties[2].role = "Contract Partner";
        return;
    }
    
    if (isMutual) {
        state.parties.forEach(p => p.role = "Disclosing Party & Receiving Party");
    } else {
        const disclosingIndex = document.querySelector('input[name="disclosing-party-radio"]:checked')?.value || "0";
        state.parties.forEach((p, idx) => {
            if (idx === parseInt(disclosingIndex)) {
                p.role = "Disclosing Party";
            } else {
                p.role = "Receiving Party";
            }
        });
    }
}

function setupEventListeners() {
    // Step Navigation
    document.getElementById("prev-btn").addEventListener("click", () => navigateWizard(-1));
    document.getElementById("next-btn").addEventListener("click", () => navigateWizard(1));
    
    document.querySelectorAll(".step-item").forEach(item => {
        item.addEventListener("click", () => {
            const step = parseInt(item.dataset.step);
            navigateWizard(step - currentStep);
        });
    });
    
    // Step 1: Select Agreement
    document.getElementById("agreement-nature").addEventListener("change", (e) => {
        state.nature = e.target.value;
        autoGenTitle();
        renderRoleIdentification();
        updatePartyRoles();
        loadMasterSchema().then(() => {
            triggerLivePreview();
        });
    });
    
    document.getElementById("agreement-category").addEventListener("change", (e) => {
        const val = e.target.value;
        document.getElementById("industry-select").value = val;
        state.industry = val;
        toggleSubSectorVisibility();
        loadPurposes();
        autoGenTitle();
        triggerLivePreview();
    });
    
    document.getElementById("agreement-type").addEventListener("change", (e) => {
        state.agreement_type = e.target.value;
        autoGenTitle();
        updatePartyRoles();
        triggerLivePreview();
    });
    
    // Step 2: Details
    document.getElementById("agreement-title-input").addEventListener("input", (e) => {
        state.agreement_title = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("effective-date-option").addEventListener("change", (e) => {
        state.effective_date = e.target.value;
        const container = document.getElementById("custom-date-container");
        container.style.display = e.target.value === "Custom Date" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("custom-effective-date-input").addEventListener("change", (e) => {
        state.custom_effective_date = e.target.value;
        triggerLivePreview();
    });
    
    // Step 3: Industry selection
    document.getElementById("industry-select").addEventListener("change", (e) => {
        state.industry = e.target.value;
        document.getElementById("agreement-category").value = e.target.value;
        toggleSubSectorVisibility();
        loadPurposes();
        autoGenTitle();
        triggerLivePreview();
    });
    
    document.getElementById("sub-sector-select").addEventListener("change", (e) => {
        state.sub_sector = e.target.value;
        autoGenTitle();
        triggerLivePreview();
    });
    
    // Step 4: Parties
    document.getElementById("parties-count").addEventListener("change", (e) => {
        const count = parseInt(e.target.value);
        adjustPartiesCount(count);
        renderPartiesForms();
        updatePartyRoles();
        triggerLivePreview();
    });
    
    // Step 6: Purposes
    document.getElementById("purpose-template-select").addEventListener("change", (e) => {
        state.selected_purpose = e.target.value;
        updatePurposePreview();
        triggerLivePreview();
    });
    
    document.getElementById("custom-purpose-textarea").addEventListener("input", (e) => {
        state.custom_purpose = e.target.value;
        triggerLivePreview();
    });
    
    // Step 7: Commercial terms
    document.getElementById("agreement-term-select").addEventListener("change", (e) => {
        state.agreement_term = e.target.value;
        document.getElementById("custom-term-container").style.display = e.target.value === "Custom" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("custom-term-input").addEventListener("input", (e) => {
        state.agreement_term = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("renewal-select").addEventListener("change", (e) => {
        state.renewal = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("notice-period-select").addEventListener("change", (e) => {
        state.notice_period = e.target.value;
        document.getElementById("custom-notice-container").style.display = e.target.value === "Custom" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("custom-notice-input").addEventListener("input", (e) => {
        state.notice_period = e.target.value;
        triggerLivePreview();
    });
    
    // Step 8: Optional Clauses
    document.querySelectorAll(".clause-opt").forEach(el => {
        el.addEventListener("change", () => {
            const activeOpts = Array.from(document.querySelectorAll(".clause-opt:checked")).map(i => i.value);
            state.optional_clauses = activeOpts;
            toggleClauseConfigPanels();
            triggerLivePreview();
        });
    });
    
    // Step 9: Clause configurations
    document.getElementById("liability-cap-select").addEventListener("change", (e) => {
        state.liability_cap = e.target.value;
        document.getElementById("custom-cap-container").style.display = e.target.value === "Custom" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("custom-cap-input").addEventListener("input", (e) => {
        state.liability_cap = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("non-sol-period").addEventListener("change", (e) => {
        state.non_solicitation_period = e.target.value;
        document.getElementById("custom-non-sol-container").style.display = e.target.value === "Custom" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("custom-non-sol-input").addEventListener("input", (e) => {
        state.non_solicitation_period = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("non-circ-period").addEventListener("change", (e) => {
        state.non_circumvention_period = e.target.value;
        document.getElementById("custom-non-circ-container").style.display = e.target.value === "Custom" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("custom-non-circ-input").addEventListener("input", (e) => {
        state.non_circumvention_period = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("data-protection-type").addEventListener("change", (e) => {
        state.data_protection_setting = e.target.value;
        triggerLivePreview();
    });
    
    // Step 10: Definitions
    document.querySelectorAll(".def-opt").forEach(el => {
        el.addEventListener("change", () => {
            const activeDefs = Array.from(document.querySelectorAll(".def-opt:checked")).map(i => i.value);
            state.optional_definitions = activeDefs;
            triggerLivePreview();
        });
    });
    
    // Step 12: Dispute Resolution
    document.getElementById("governing-law-select").addEventListener("change", (e) => {
        state.dispute_resolution.governing_law = e.target.value;
        document.getElementById("state-select-container").style.display = e.target.value === "India" ? "flex" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("governing-state-select").addEventListener("change", (e) => {
        state.dispute_resolution.state = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("dispute-mechanism").addEventListener("change", (e) => {
        state.dispute_resolution.mechanism = e.target.value;
        document.getElementById("arbitration-options-container").style.display = e.target.value === "Arbitration" ? "block" : "none";
        triggerLivePreview();
    });
    
    document.getElementById("arbitration-institution").addEventListener("change", (e) => {
        state.dispute_resolution.institution = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("arbitration-seat").addEventListener("change", (e) => {
        state.dispute_resolution.seat = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("arbitrators-count").addEventListener("change", (e) => {
        state.dispute_resolution.arbitrators = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("pre-arbitration-condition").addEventListener("change", (e) => {
        state.dispute_resolution.pre_condition = e.target.value;
        triggerLivePreview();
    });
    
    // Step 13: Execution Details
    document.getElementById("electronic-signatures").addEventListener("change", (e) => {
        state.execution.signatures = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("execution-counterparts").addEventListener("change", (e) => {
        state.execution.counterparts = e.target.value;
        triggerLivePreview();
    });
    
    document.getElementById("witness-required").addEventListener("change", (e) => {
        state.execution.witness = e.target.value;
        triggerLivePreview();
    });
    // Full Screen Preview Toggle
    const fullscreenToggle = document.getElementById("fullscreen-preview-toggle");
    if (fullscreenToggle) {
        fullscreenToggle.addEventListener("click", () => {
            const workspace = document.querySelector(".workspace-split");
            workspace.classList.toggle("fullscreen-preview");
            
            if (workspace.classList.contains("fullscreen-preview")) {
                fullscreenToggle.textContent = "🗜️ Exit Full Screen";
                fullscreenToggle.classList.add("btn-primary");
            } else {
                fullscreenToggle.textContent = "🔍 Toggle Full Screen";
                fullscreenToggle.classList.remove("btn-primary");
            }
        });
    }

    // Preview direct editing
    const previewToggle = document.getElementById("edit-preview-toggle");
    const previewDiv = document.getElementById("contract-live-preview");
    previewToggle.addEventListener("click", () => {
        isEditingDirectly = !isEditingDirectly;
        if (isEditingDirectly) {
            previewDiv.contentEditable = "true";
            previewDiv.focus();
            previewToggle.textContent = "💾 Save Manual Text";
            previewToggle.classList.add("btn-primary");
            // Store text
            manualContractText = previewDiv.innerText;
        } else {
            previewDiv.contentEditable = "false";
            previewToggle.textContent = "✏️ Edit Text Directly";
            previewToggle.classList.remove("btn-primary");
            // Keep modified manual text
            manualContractText = previewDiv.innerText;
        }
    });
    
    previewDiv.addEventListener("input", () => {
        if (isEditingDirectly) {
            manualContractText = previewDiv.innerText;
        }
    });
    
    // Step 15 Exports
    document.getElementById("download-docx-btn").addEventListener("click", downloadDOCX);
    document.getElementById("ai-risk-btn").addEventListener("click", runRiskAudit);
    document.getElementById("redline-btn").addEventListener("click", applyRedlines);
    
    document.getElementById("close-risk-sidebar").addEventListener("click", () => {
        document.getElementById("risk-sidebar").classList.remove("open");
    });
}

function autoGenTitle() {
    let typeName = state.agreement_type;
    let natureName = state.nature;
    
    let genTitle = "";
    if (typeName === "NDA") {
        genTitle = `${natureName} Non-Disclosure Agreement`.toUpperCase();
    } else {
        genTitle = `${typeName}`.toUpperCase();
    }
    
    if (state.industry === "Renewable Energy" && state.sub_sector) {
        genTitle += ` - ${state.sub_sector.toUpperCase()} PROJECT`;
    }
    
    state.agreement_title = genTitle;
    document.getElementById("agreement-title-input").value = genTitle;
}

function toggleSubSectorVisibility() {
    const sub = document.getElementById("sub-sector-container");
    sub.style.display = state.industry === "Renewable Energy" ? "block" : "none";
}

function adjustPartiesCount(count) {
    if (count === 3 && state.parties.length === 2) {
        state.parties.push({
            name: "Gamma Development",
            entity_type: "Private Limited Company",
            reg_number: "REG-555555",
            gst_number: "29CCCCC3333C3Z3",
            pan_number: "CCCCC3333C",
            address: "909 Green Valley Road, Bangalore 560001",
            email: "partner@gammadev.com",
            phone: "+91-9877766655",
            sig_name: "Amit Kumar",
            sig_designation: "Legal Head",
            role: "Disclosing Party & Receiving Party"
        });
    } else if (count === 2 && state.parties.length === 3) {
        state.parties.pop();
    }
}

function renderRoleIdentification() {
    const container = document.getElementById("role-identification-content");
    
    if (state.nature === "Mutual") {
        container.innerHTML = `
            <div class="preview-box">
                <h4>System Logic</h4>
                <p>Mutual NDA Selected: Roles are pre-assigned to all parties.</p>
                <table style="width:100%; border-collapse:collapse; margin-top:8px;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.1); text-align:left;">
                            <th style="padding:6px 0;">Party</th>
                            <th style="padding:6px 0;">Assigned Role</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td style="padding:6px 0;">Party A</td><td style="padding:6px 0; color:var(--accent);">Disclosing & Receiving Party</td></tr>
                        <tr><td style="padding:6px 0;">Party B</td><td style="padding:6px 0; color:var(--accent);">Disclosing & Receiving Party</td></tr>
                    </tbody>
                </table>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="form-group">
                <label>Which party is Disclosing Confidential Information?</label>
                <div style="display:flex; gap:16px; margin-top:8px;">
                    <label style="cursor:pointer;"><input type="radio" name="disclosing-party-radio" value="0" checked> Party A (Disclosing)</label>
                    <label style="cursor:pointer;"><input type="radio" name="disclosing-party-radio" value="1"> Party B (Disclosing)</label>
                </div>
            </div>
        `;
        
        document.querySelectorAll('input[name="disclosing-party-radio"]').forEach(el => {
            el.addEventListener("change", () => {
                updatePartyRoles();
                triggerLivePreview();
            });
        });
    }
}

function updatePurposePreview() {
    const previewBox = document.getElementById("purpose-preview-box");
    if (!state.selected_purpose) {
        previewBox.style.display = "none";
        return;
    }
    
    const purp = purposeDatabase[state.industry]?.[state.selected_purpose];
    if (purp) {
        previewBox.style.display = "block";
        document.getElementById("db-recital-preview").textContent = purp.recitals?.join(" ") || "N/A";
        document.getElementById("db-purpose-preview").textContent = purp.purpose_definition || "N/A";
        document.getElementById("db-ci-preview").textContent = purp.confidential_information_expansion?.join(" ") || "N/A";
    } else {
        previewBox.style.display = "none";
    }
}

function toggleClauseConfigPanels() {
    const cList = state.optional_clauses;
    
    const showDp = cList.includes("Data Protection");
    const showLol = cList.includes("Limitation of Liability");
    const showSol = cList.includes("Non-Solicitation");
    const showCirc = cList.includes("Non-Circumvention");
    
    document.getElementById("config-data-protection").style.display = showDp ? "block" : "none";
    document.getElementById("config-limitation-of-liability").style.display = showLol ? "block" : "none";
    document.getElementById("config-non-solicitation").style.display = showSol ? "block" : "none";
    document.getElementById("config-non-circumvention").style.display = showCirc ? "block" : "none";
    
    const noConfig = !showDp && !showLol && !showSol && !showCirc;
    document.getElementById("no-clause-config-message").style.display = noConfig ? "block" : "none";
}

function navigateWizard(offset) {
    const nextStep = currentStep + offset;
    if (nextStep < 1 || nextStep > totalSteps) return;
    
    // Save state or perform validation if needed
    document.getElementById(`panel-${currentStep}`).classList.remove("active");
    document.querySelector(`.step-item[data-step="${currentStep}"]`).classList.remove("active");
    if (currentStep < nextStep) {
        document.querySelector(`.step-item[data-step="${currentStep}"]`).classList.add("completed");
    }
    
    currentStep = nextStep;
    document.getElementById(`panel-${currentStep}`).classList.add("active");
    document.querySelector(`.step-item[data-step="${currentStep}"]`).classList.add("active");
    
    // Toggle AI Enhancement specific layout
    const workspace = document.querySelector(".workspace-split");
    if (currentStep === 15) {
        workspace.classList.add("ai-enhancement-mode");
    } else {
        workspace.classList.remove("ai-enhancement-mode");
    }
    
    // Disable prev/next
    document.getElementById("prev-btn").disabled = currentStep === 1;
    document.getElementById("next-btn").textContent = currentStep === totalSteps ? "Finish" : "Next →";
    
    // Update headers
    const titles = [
        "Select Agreement", "Agreement Details", "Industry Selection", "Party Details",
        "Role Identification", "Purpose & Recitals", "Commercial Terms", "Clause Library",
        "Clause Configuration", "Definitions", "Notice Details", "Dispute Resolution",
        "Execution Details", "AI Review Summary", "Generate & Export"
    ];
    document.getElementById("page-title").textContent = titles[currentStep - 1];
    
    if (currentStep === 14) {
        renderSummaryDashboard();
    }
}

function renderSummaryDashboard() {
    const container = document.getElementById("summary-dashboard-content");
    
    const partiesStr = state.parties.map(p => `${p.name} (${p.role})`).join(" vs ");
    const clausesStr = ["Mandatory Core", ...state.optional_clauses].join(", ");
    
    // Compute a simulated risk score
    let riskLevel = "Low";
    let riskClass = "risk-low";
    if (state.liability_cap === "No Cap") {
        riskLevel = "High";
        riskClass = "risk-high";
    }
    if (state.optional_clauses.length < 3) {
        riskLevel = "Medium";
        riskClass = "risk-medium";
    }
    
    container.innerHTML = `
        <div class="summary-row">
            <span>Agreement Type:</span>
            <span class="summary-value">${state.agreement_type} (${state.nature})</span>
        </div>
        <div class="summary-row">
            <span>Parties:</span>
            <span class="summary-value">${partiesStr}</span>
        </div>
        <div class="summary-row">
            <span>Industry:</span>
            <span class="summary-value">${state.industry} ${state.sub_sector ? `(${state.sub_sector})` : ""}</span>
        </div>
        <div class="summary-row">
            <span>Selected Purpose:</span>
            <span class="summary-value">${state.selected_purpose || "Custom Purpose"}</span>
        </div>
        <div class="summary-row">
            <span>Commercial Term:</span>
            <span class="summary-value">${state.agreement_term} (${state.renewal})</span>
        </div>
        <div class="summary-row">
            <span>Active Clauses:</span>
            <span class="summary-value">${clausesStr}</span>
        </div>
        <div class="summary-row">
            <span>Dispute seat:</span>
            <span class="summary-value">${state.dispute_resolution.seat} (${state.dispute_resolution.governing_law})</span>
        </div>
        <div class="summary-row">
            <span>Simulated Risk Rating:</span>
            <span class="risk-tag ${riskClass}">${riskLevel} Risk</span>
        </div>
    `;
}

function triggerLivePreview() {
    if (isEditingDirectly) return; // Prevent overwriting manual text
    
    fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(state)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            const previewDiv = document.getElementById("contract-live-preview");
            previewDiv.innerHTML = formatContractToHTML(data.contract_text, state.agreement_title);
            manualContractText = data.contract_text;
            
            // Update document headers/footers dynamically
            const headerType = document.getElementById("doc-header-type");
            if (headerType) {
                headerType.textContent = `${state.agreement_type} DRAFT - ${state.nature.toUpperCase()}`;
            }
            
            const footerPage = document.getElementById("doc-footer-page");
            if (footerPage) {
                const estPages = Math.max(1, Math.ceil(data.contract_text.length / 2800));
                footerPage.textContent = `Page 1 of ${estPages}`;
            }
        }
    })
    .catch(err => console.error("Error updating preview:", err));
}

function formatContractToHTML(text, title) {
    let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    let lines = html.split('\n');
    let formattedLines = [];
    let skipTitle = true;
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) {
            formattedLines.push("<br>");
            continue;
        }
        
        if (skipTitle && line.toUpperCase() === title.toUpperCase()) {
            skipTitle = false;
            formattedLines.push(`<div style="text-align: center; font-weight: bold; font-size: 14pt; margin-bottom: 12pt; text-transform: uppercase;">${line}</div>`);
            continue;
        }
        
        if (line === "RECITALS" || line === "BY AND BETWEEN" || line === "AND" || line.startsWith("IN WITNESS WHEREOF")) {
            formattedLines.push(`<div style="text-align: center; font-weight: bold; margin-bottom: 6pt;">${line}</div>`);
            continue;
        }
        
        if (/^(\d+)\.\s+[A-Z\s\-]+$/.test(line) || (/^[A-Z][A-Z\s]{4,30}$/.test(line) && line.length < 40)) {
            formattedLines.push(`<div style="font-weight: bold; text-align: left; margin-top: 12pt; margin-bottom: 6pt;">${line}</div>`);
            continue;
        }
        
        if (/^(\d+\.\d+)\s+[A-Za-z\s\-]+$/.test(line) && line.split(' ').length < 8 && !line.endsWith('.')) {
            formattedLines.push(`<div style="font-weight: bold; text-align: left; margin-top: 6pt; margin-bottom: 3pt;">${line}</div>`);
            continue;
        }
        
        if (/^\([a-zivx]+\)/.test(line)) {
            formattedLines.push(`<div style="margin-left: 0.25in; text-align: justify; text-indent: -0.25in; padding-left: 0.25in;">${line}</div>`);
            continue;
        }
        
        let defMatch = line.match(/^(\d+\.\d+(?:\.\d+)?)\s+(&quot;[^&]+&quot;)/);
        if (defMatch) {
            let num = defMatch[1];
            let term = defMatch[2];
            let remainder = line.substring(num.length + term.length + 1).trim();
            formattedLines.push(`<div style="text-align: justify;">${num} <strong>${term}</strong> ${remainder}</div>`);
            continue;
        }
        
        formattedLines.push(`<div style="text-align: justify;">${line}</div>`);
    }
    
    return formattedLines.join('\n');
}

function downloadDOCX() {
    const text = manualContractText || document.getElementById("contract-live-preview").innerText;
    
    fetch("/api/export/docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title: state.agreement_title,
            text: text
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Export failed");
        return res.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${state.agreement_title.toLowerCase().replace(/[^a-z0-9]+/g, '_')}.docx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast("DOCX file generated and download started!", "success");
    })
    .catch(err => showToast("Failed to download DOCX: " + err.message, "error"));
}

function runRiskAudit() {
    const text = manualContractText || document.getElementById("contract-live-preview").innerText;
    const sidebar = document.getElementById("risk-sidebar");
    const list = document.getElementById("risk-list");
    
    list.innerHTML = "<p>Scanning contract clauses...</p>";
    sidebar.classList.add("open");
    
    fetch("/api/risk-review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success" && data.risks.length > 0) {
            list.innerHTML = "";
            data.risks.forEach(r => {
                const card = document.createElement("div");
                card.className = `risk-card ${r.severity.toLowerCase()}`;
                card.innerHTML = `
                    <div class="risk-header">
                        <span>${r.clause}</span>
                        <span class="risk-tag risk-${r.severity.toLowerCase()}">${r.severity}</span>
                    </div>
                    <p><strong>Issue:</strong> ${r.issue}</p>
                    <div class="risk-suggestion">
                        <strong>Correction:</strong> ${r.suggestion}
                        <button class="btn btn-mini apply-correction-btn" style="margin-top:6px; display:block;">Apply Correction</button>
                    </div>
                `;
                list.appendChild(card);
            });
            
            // Wire correction buttons
            document.querySelectorAll(".apply-correction-btn").forEach((btn, idx) => {
                btn.addEventListener("click", () => {
                    const r = data.risks[idx];
                    applyRiskCorrection(r);
                    btn.disabled = true;
                    btn.textContent = "Applied ✓";
                });
            });
        } else {
            list.innerHTML = "<p class='text-success'>✓ No critical risks identified in this configuration.</p>";
        }
    })
    .catch(err => {
        list.innerHTML = `<p class='text-danger'>Audit failed: ${err.message}</p>`;
    });
}

function applyRiskCorrection(risk) {
    const previewDiv = document.getElementById("contract-live-preview");
    let currentText = previewDiv.innerText;
    
    if (risk.clause === "Limitation of Liability") {
        state.liability_cap = "INR 10 Lakhs";
        document.getElementById("liability-cap-select").value = "INR 10 Lakhs";
        triggerLivePreview();
    } else if (risk.clause === "Dispute Resolution") {
        state.dispute_resolution.pre_condition = "Direct Negotiation (30 Days)";
        document.getElementById("pre-arbitration-condition").value = "Direct Negotiation (30 Days)";
        triggerLivePreview();
    } else if (risk.clause === "Non-Solicitation") {
        state.non_solicitation_period = "1 Year";
        document.getElementById("non-sol-period").value = "1 Year";
        triggerLivePreview();
    } else if (risk.clause === "Data Protection") {
        state.data_protection_setting = "DPDP Act, 2023";
        document.getElementById("data-protection-type").value = "DPDP Act, 2023";
        triggerLivePreview();
    }
}

function applyRedlines() {
    // Highlights the preview area with minor simulated redline highlights (green edits)
    const previewDiv = document.getElementById("contract-live-preview");
    let html = previewDiv.innerHTML;
    
    // Replace some patterns with redlines
    if (html.includes("No Cap")) {
        html = html.replace("No Cap", "<span style='text-decoration: line-through; color: #EF4444;'>No Cap</span> <span style='color: #10B981; font-weight: bold;'>INR 10 Lakhs</span>");
        previewDiv.innerHTML = html;
        showToast("Redlines suggested! Review highlighted changes on the A4 page preview.", "info");
    } else {
        showToast("Document matches standard parameters. No redline suggestions found.", "success");
    }
}

// Structured Schema loading & rendering
let masterSchema = {};

function loadMasterSchema() {
    const isMutual = state.nature === "Mutual";
    return fetch(`/api/master-schema?mutual=${isMutual}`)
        .then(res => res.json())
        .then(data => {
            masterSchema = data;
            renderDynamicDefinitionsList();
            renderDynamicClausesList();
        })
        .catch(err => console.error("Error loading master schema:", err));
}

function renderDynamicDefinitionsList() {
    const mandatoryList = document.getElementById("mandatory-definitions-list");
    const optionalList = document.getElementById("optional-definitions-list");
    if (!mandatoryList || !optionalList) return;
    
    mandatoryList.innerHTML = "";
    optionalList.innerHTML = "";
    
    const defs = masterSchema["1_DEFINITIONS"] || {};
    const sortedKeys = Object.keys(defs).sort();
    
    const optionalTermNames = ["Introduced Contact", "Restricted Personnel", "Business Opportunity", "Security Incident", "Force Majeure Event"];
    
    sortedKeys.forEach(key => {
        const item = defs[key];
        const term = item.term;
        const definition = item.definition;
        
        const isOptional = optionalTermNames.includes(term);
        
        const li = document.createElement("li");
        li.style.flexDirection = "column";
        li.style.alignItems = "flex-start";
        li.style.width = "100%";
        li.style.marginBottom = "14px";
        
        if (isOptional) {
            const isChecked = state.optional_definitions.includes(term);
            li.innerHTML = `
                <label style="font-weight: 600; display: flex; align-items: center; gap: 8px;">
                    <input type="checkbox" value="${term}" class="def-opt" ${isChecked ? "checked" : ""}> ${term}
                </label>
                <div class="clause-full-text-preview">${definition}</div>
            `;
        } else {
            li.innerHTML = `
                <label style="font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
                    <input type="checkbox" checked disabled> ${term}
                </label>
                <div class="clause-full-text-preview">${definition}</div>
            `;
        }
        
        if (isOptional) {
            optionalList.appendChild(li);
        } else {
            mandatoryList.appendChild(li);
        }
    });
    
    // Re-wire event listeners for .def-opt checkboxes
    document.querySelectorAll(".def-opt").forEach(el => {
        el.addEventListener("change", () => {
            const activeDefs = Array.from(document.querySelectorAll(".def-opt:checked")).map(i => i.value);
            state.optional_definitions = activeDefs;
            triggerLivePreview();
        });
    });
}

function renderDynamicClausesList() {
    const mandatoryList = document.getElementById("mandatory-clauses-list");
    const optionalList = document.getElementById("optional-clauses-list");
    if (!mandatoryList || !optionalList) return;
    
    mandatoryList.innerHTML = "";
    optionalList.innerHTML = "";
    
    const mandatoryKeys = [
        { key: "2_EXCLUSIONS_FROM_CONFIDENTIAL_INFORMATION", title: "Exclusions from Confidential Information" },
        { key: "3_CONFIDENTIALITY_OBLIGATIONS", title: "Confidentiality Obligations" },
        { key: "4_PERMITTED_DISCLOSURES", title: "Permitted Disclosures" },
        { key: "5_NON_USE_OBLIGATIONS", title: "Non-Use Obligations" },
        { key: "6_COMPELLED_DISCLOSURE", title: "Compelled Disclosure" },
        { key: "7_RETURN_OR_DESTRUCTION_OF_CONFIDENTIAL_INFORMATION", title: "Return or Destruction of Confidential Information" },
        { key: "8_INTELLECTUAL_PROPERTY_RIGHTS_AND_NO_LICENSE", title: "Intellectual Property Rights and No License" },
        { key: "10_NO_WARRANTY", title: "No Warranty" },
        { key: "11_TERM_AND_TERMINATION", title: "Term and Termination" },
        { key: "12_REMEDIES_AND_INJUNCTIVE_RELIEF", title: "Remedies and Injunctive Relief" }
    ];
    
    const optionalKeys = [
        { key: "9_DATA_PROTECTION_AND_INFORMATION_SECURITY", title: "Data Protection", value: "Data Protection" },
        { key: "13_LIMITATION_OF_LIABILITY", title: "Limitation of Liability", value: "Limitation of Liability" },
        { key: "14_INDEMNITY", title: "Indemnity", value: "Indemnity" },
        { key: "15_NON_CIRCUMVENTION_AND_NON_SOLICITATION", title: "Non-Solicitation", value: "Non-Solicitation" },
        { key: "15_NON_CIRCUMVENTION_AND_NON_SOLICITATION", title: "Non-Circumvention", value: "Non-Circumvention" },
        { key: "16_PUBLIC_ANNOUNCEMENTS", title: "Public Announcements", value: "Public Announcements" }
    ];
    
    // Render Mandatory
    mandatoryKeys.forEach(m => {
        const clauseData = masterSchema[m.key] || {};
        let text = "";
        if (m.key === "2_EXCLUSIONS_FROM_CONFIDENTIAL_INFORMATION") {
            const sub21 = clauseData["2.1"] || {};
            if (sub21.a) {
                text = "Confidential Information shall not include: " + Object.keys(sub21).map(k => `(${k}) ${sub21[k]}`).join("; ");
            } else {
                text = sub21.text || "";
            }
            if (clauseData["2.2"]) text += "\n\n" + (clauseData["2.2"].text || "");
        } else {
            text = Object.keys(clauseData).sort().map(k => clauseData[k]).join("\n\n");
        }
        
        const li = document.createElement("li");
        li.style.flexDirection = "column";
        li.style.alignItems = "flex-start";
        li.style.width = "100%";
        li.style.marginBottom = "14px";
        li.innerHTML = `
            <label style="font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
                <input type="checkbox" checked disabled> ${m.title}
            </label>
            <div class="clause-full-text-preview">${text}</div>
        `;
        mandatoryList.appendChild(li);
    });
    
    // Render Optional
    optionalKeys.forEach(o => {
        const clauseData = masterSchema[o.key] || {};
        let text = "";
        if (o.value === "Non-Solicitation") {
            text = Object.keys(clauseData).sort()
                .map(k => clauseData[k])
                .filter(txt => txt.toLowerCase().includes("solicit") || txt.toLowerCase().includes("personnel"))
                .join("\n\n");
        } else if (o.value === "Non-Circumvention") {
            text = Object.keys(clauseData).sort()
                .map(k => clauseData[k])
                .filter(txt => txt.toLowerCase().includes("circumvent") || txt.toLowerCase().includes("bypass"))
                .join("\n\n");
        } else {
            text = Object.keys(clauseData).sort().map(k => clauseData[k]).join("\n\n");
        }
        
        const isChecked = state.optional_clauses.includes(o.value);
        
        const li = document.createElement("li");
        li.style.flexDirection = "column";
        li.style.alignItems = "flex-start";
        li.style.width = "100%";
        li.style.marginBottom = "14px";
        li.innerHTML = `
            <label style="font-weight: 600; display: flex; align-items: center; gap: 8px;">
                <input type="checkbox" value="${o.value}" class="clause-opt" ${isChecked ? "checked" : ""}> ${o.title}
            </label>
            <div class="clause-full-text-preview">${text}</div>
        `;
        optionalList.appendChild(li);
    });
    
    // Re-wire event listeners for .clause-opt checkboxes
    document.querySelectorAll(".clause-opt").forEach(el => {
        el.addEventListener("change", () => {
            const activeOpts = Array.from(document.querySelectorAll(".clause-opt:checked")).map(i => i.value);
            state.optional_clauses = activeOpts;
            toggleClauseConfigPanels();
            triggerLivePreview();
        });
    });
}

// Custom Premium Toast Notifications Utility
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✨";
    else if (type === "error") icon = "🚨";
    else if (type === "warning") icon = "⚠️";
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
        <span class="toast-close">&times;</span>
    `;
    
    container.appendChild(toast);
    
    const closeBtn = toast.querySelector(".toast-close");
    closeBtn.addEventListener("click", () => {
        removeToast(toast);
    });
    
    // Auto-remove after 4.5 seconds
    setTimeout(() => {
        removeToast(toast);
    }, 4500);
}

function removeToast(toast) {
    if (!toast || !toast.parentNode) return;
    toast.style.animation = "toastOut 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards";
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 300);
}

// AI Enhancement Workflow
let currentContractV2Text = "";

document.addEventListener('DOMContentLoaded', () => {
    const enhanceBtn = document.getElementById('enhance-ai-btn');
    if (enhanceBtn) {
        enhanceBtn.addEventListener('click', enhanceContractWithAI);
    }
    
    const downloadV1Btn = document.getElementById('download-docx-btn-v1-top');
    if (downloadV1Btn) {
        downloadV1Btn.addEventListener('click', downloadDOCX);
    }
    
    const downloadAIBtnTop = document.getElementById('download-ai-docx-btn-top');
    if (downloadAIBtnTop) {
        downloadAIBtnTop.addEventListener('click', () => {
            triggerDocxExport(currentContractV2Text, state.agreement_title + " (AI-Reformed)");
        });
    }
    
    const toggleCompBtn = document.getElementById('toggle-comparison-btn');
    if (toggleCompBtn) {
        toggleCompBtn.addEventListener('click', () => {
            const v1Page = document.getElementById('v1-page');
            if (v1Page.style.display === 'none') {
                v1Page.style.display = 'block';
                toggleCompBtn.innerText = '⚖️ Disable Comparison View';
            } else {
                v1Page.style.display = 'none';
                toggleCompBtn.innerText = '⚖️ Enable Comparison View';
            }
        });
    }
});

function enhanceContractWithAI() {
    const promptInput = document.getElementById('ai-user-prompt');
    const loadingInd = document.getElementById('ai-loading-status');
    const enhanceBtn = document.getElementById('enhance-ai-btn');
    const v2Page = document.getElementById('v2-page');
    const v2Preview = document.getElementById('ai-reformed-preview');
    const toggleCompBtn = document.getElementById('toggle-comparison-btn');
    
    const userPrompt = promptInput.value.trim() || "Improve drafting quality and enforceability.";
    
    enhanceBtn.style.display = 'none';
    loadingInd.style.display = 'block';
    
    // Ensure we send the most up-to-date manual contract text
    fetch('/api/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contract_type: state.agreement_type,
            contract_json: state,
            rule_based_contract: manualContractText,
            user_prompt: userPrompt
        })
    })
    .then(res => res.json())
    .then(data => {
        enhanceBtn.style.display = 'block';
        loadingInd.style.display = 'none';
        
        if (data.status === 'success') {
            currentContractV2Text = data.ai_reformed_contract;
            
            // Show V2 Panel
            v2Page.style.display = 'block';
            
            // Show comparison button
            toggleCompBtn.style.display = 'inline-block';
            toggleCompBtn.innerText = '⚖️ Disable Comparison View';
            
            v2Preview.innerHTML = formatContractToHTML(currentContractV2Text, state.agreement_title);
            
            showToast('AI Enhancement Complete!', 'success');
        } else {
            showToast('AI Enhancement Failed. ' + (data.detail || 'Check logs.'), 'error');
        }
    })
    .catch(err => {
        enhanceBtn.style.display = 'block';
        loadingInd.style.display = 'none';
        showToast('Network error during AI Enhancement.', 'error');
        console.error(err);
    });
}

function triggerDocxExport(text, title) {
    if (!text) return;
    
    fetch("/api/export/docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title: title || "LexForge_Contract",
            text: text
        })
    })
    .then(res => res.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = (title || "LexForge_Contract").replace(/ /g, '_') + ".docx";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(err => {
        console.error("Export error:", err);
        showToast("Error exporting document", "error");
    });
}
