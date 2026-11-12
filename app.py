import os
import io
import json
import pandas as pd
import streamlit as st
from pypdf import PdfReader

from state import VDRAnalysisState, RiskItem
from doc_parser import DocumentParser
from orchestrator import run_contract_swarm, run_vdr_zip_audit

# Auto-generate sample VDR contracts on first boot (required for Streamlit Cloud)
_vdr_dir = "vdr_docs"
_zip_path = os.path.join(_vdr_dir, "VDR_Corporate_Contracts_Package.zip")
if not os.path.exists(_zip_path):
    try:
        from generate_samples import generate_sample_contracts
        generate_sample_contracts()
    except Exception:
        pass

st.set_page_config(
    page_title="EY Strategy and Transactions - ContractSwarm",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom EY Corporate Dark Styling (Pure Black BG, No emojis, no symbols, zero top gap)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Canvas and Black Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background-color: #0A0A0C !important;
        color: #F4F4F6 !important;
    }

    /* ELIMINATE TOP GAP COMPLETELY */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 1.5rem !important;
        min-height: 0px !important;
    }

    .main .block-container,
    div[data-testid="stMainBlockContainer"],
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stSidebarHeader"] {
        height: 0px !important;
        padding-top: 0px !important;
    }

    div[data-testid="stSidebarContent"] {
        padding-top: 1rem !important;
    }
    
    /* Top EY Yellow Brand Accent Bar */
    .ey-top-accent {
        height: 4px;
        background-color: #FFE600;
        width: 100%;
        margin: 0 0 16px 0;
        padding: 0;
    }
    
    /* EY Corporate Masthead */
    .ey-masthead {
        background-color: #121216;
        color: #FFFFFF;
        padding: 22px 28px;
        border-radius: 2px;
        margin-bottom: 22px;
        border-left: 5px solid #FFE600;
        border-top: 1px solid #22222A;
        border-right: 1px solid #22222A;
        border-bottom: 1px solid #22222A;
    }
    
    .ey-brand-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        color: #FFE600;
        margin-bottom: 6px;
    }
    
    .ey-main-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin: 0 0 4px 0;
    }
    
    .ey-sub-title {
        font-size: 13px;
        color: #9E9EA8;
        margin: 0;
        font-weight: 400;
    }
    
    /* KPI Metric Cards */
    .ey-kpi-container {
        display: flex;
        gap: 16px;
        margin-bottom: 22px;
    }
    
    .ey-kpi-card {
        flex: 1;
        background-color: #121216;
        border: 1px solid #24242E;
        border-top: 3px solid #3E3E4C;
        border-radius: 2px;
        padding: 16px 18px;
    }
    
    .ey-kpi-card-high {
        border-top: 3px solid #DC2626 !important;
    }
    
    .ey-kpi-card-medium {
        border-top: 3px solid #F59E0B !important;
    }
    
    .ey-kpi-card-status {
        border-top: 3px solid #FFE600 !important;
    }
    
    .ey-kpi-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        color: #9E9EA8;
        margin-bottom: 6px;
    }
    
    .ey-kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.1;
    }
    
    .ey-kpi-subtext {
        font-size: 11px;
        color: #6C6C78;
        margin-top: 4px;
    }
    
    /* Executive Summary Box */
    .ey-summary-box {
        background-color: #121216;
        border: 1px solid #24242E;
        border-left: 4px solid #FFE600;
        border-radius: 2px;
        padding: 18px 22px;
        margin-bottom: 22px;
    }
    
    .ey-summary-title {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        color: #FFE600;
        margin-bottom: 8px;
    }
    
    .ey-summary-text {
        font-size: 14px;
        line-height: 1.6;
        color: #D4D4D8;
        margin: 0;
    }
    
    /* Detail Finding Cards */
    .ey-finding-card {
        background-color: #121216;
        border: 1px solid #24242E;
        border-radius: 2px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    
    .ey-badge {
        display: inline-block;
        padding: 2px 7px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 2px;
        margin-right: 8px;
    }
    
    .ey-badge-high {
        background-color: #DC2626;
        color: #FFFFFF;
    }
    
    .ey-badge-medium {
        background-color: #F59E0B;
        color: #000000;
    }
    
    .ey-badge-low {
        background-color: #2563EB;
        color: #FFFFFF;
    }
    
    .ey-badge-workstream {
        background-color: #24242E;
        color: #FFE600;
    }
    
    /* Table Styling */
    .ey-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 13px;
    }
    
    .ey-table th {
        background-color: #17171C;
        color: #FFE600;
        text-align: left;
        padding: 10px 14px;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid #24242E;
    }
    
    .ey-table td {
        padding: 12px 14px;
        border: 1px solid #24242E;
        vertical-align: top;
        color: #D4D4D8;
        background-color: #121216;
    }
    
    .ey-table tr:nth-child(even) td {
        background-color: #0E0E12;
    }
    
    .ey-section-title {
        font-size: 15px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #FFFFFF;
        margin: 22px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #24242E;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0E0E12 !important;
        border-right: 1px solid #24242E !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #E4E4E7 !important;
    }
    
    /* High-Contrast EY Action Button */
    div.stButton > button {
        background-color: #FFE600 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 2px !important;
        border: none !important;
        padding: 10px 24px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-size: 12px !important;
        width: 100% !important;
    }
    
    div.stButton > button:hover {
        background-color: #FFF066 !important;
        color: #000000 !important;
        border: none !important;
    }
    
    /* Tab Styling */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 12px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        color: #71717A !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFE600 !important;
        border-bottom-color: #FFE600 !important;
        border-bottom-width: 3px !important;
    }

    /* Inputs and text areas in dark mode */
    textarea, input, select {
        background-color: #121216 !important;
        color: #FFFFFF !important;
        border: 1px solid #24242E !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Yellow Brand Accent Bar (placed immediately at top with 0 gap)
st.markdown('<div class="ey-top-accent"></div>', unsafe_allow_html=True)

# EY Corporate Masthead
st.markdown("""
<div class="ey-masthead">
    <div class="ey-brand-label">EY Strategy and Transactions | M&A Due Diligence</div>
    <div class="ey-main-title">ContractSwarm Autonomous Diligence Fabric</div>
    <div class="ey-sub-title">Multi-agent cognitive orchestration for virtual data room liability audits, contractual risk indexing, and deal governance.</div>
</div>
""", unsafe_allow_html=True)

parser = DocumentParser()

st.sidebar.markdown("""
<div style="padding-bottom: 12px; border-bottom: 1px solid #24242E; margin-bottom: 16px;">
    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #FFE600;">Diligence Engagement</div>
    <div style="font-size: 12px; color: #9E9EA8; margin-top: 4px;">Engagement: Project Horizon Due Diligence</div>
    <div style="font-size: 12px; color: #9E9EA8;">Advisor: EY Strategy and Transactions</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Document Intake Mode")
input_mode = st.sidebar.radio(
    "Select Intake Source",
    [
        "Preloaded VDR ZIP Package",
        "Upload VDR ZIP Package",
        "Preloaded Individual PDF",
        "Upload Single PDF",
        "Direct Text Input"
    ],
    label_visibility="collapsed"
)

active_contracts: dict[str, str] = {}
active_package_name = "VDR Target Batch"

vdr_dir = "vdr_docs"
sample_pdfs = []
sample_zips = []
if os.path.exists(vdr_dir):
    sample_pdfs = sorted([f for f in os.listdir(vdr_dir) if f.endswith(".pdf")])
    sample_zips = sorted([f for f in os.listdir(vdr_dir) if f.endswith(".zip")])

if input_mode == "Preloaded VDR ZIP Package":
    if sample_zips:
        chosen_zip = st.sidebar.selectbox("VDR ZIP Selection", sample_zips)
        active_package_name = chosen_zip
        zip_full_path = os.path.join(vdr_dir, chosen_zip)
        active_contracts = parser.parse_vdr_zip(zip_full_path)
    else:
        st.sidebar.warning("No sample ZIP packages found in vdr_docs.")

elif input_mode == "Upload VDR ZIP Package":
    uploaded_zip = st.sidebar.file_uploader("Upload Corporate Contracts ZIP Archive", type=["zip"])
    if uploaded_zip is not None:
        active_package_name = uploaded_zip.name
        active_contracts = parser.parse_vdr_zip(uploaded_zip)

elif input_mode == "Preloaded Individual PDF":
    if sample_pdfs:
        chosen_pdf = st.sidebar.selectbox("PDF Selection", sample_pdfs)
        active_package_name = chosen_pdf
        pdf_full_path = os.path.join(vdr_dir, chosen_pdf)
        txt = parser.parse_file(pdf_full_path)
        active_contracts = {chosen_pdf: txt}
    else:
        st.sidebar.warning("No sample PDFs found.")

elif input_mode == "Upload Single PDF":
    uploaded_pdf = st.sidebar.file_uploader("Upload Single PDF Contract", type=["pdf"])
    if uploaded_pdf is not None:
        active_package_name = uploaded_pdf.name
        txt = parser.parse_pdf_bytes(uploaded_pdf.read(), uploaded_pdf.name)
        active_contracts = {uploaded_pdf.name: txt}

elif input_mode == "Direct Text Input":
    active_package_name = "Manual Contract Excerpt"
    default_text = (
        "CONFIDENTIAL - MERGER AGREEMENT\n\n"
        "SECTION 4.1 INDEMNIFICATION\n"
        "Target agrees to indemnify and hold harmless the Buyer against all claims without limitation.\n\n"
        "SECTION 7.3 CHANGE OF CONTROL\n"
        "Transaction triggers change of control rights and debt acceleration.\n\n"
        "SECTION 9.2 LIQUIDATED DAMAGES\n"
        "Delay in completion incurs liquidated damages of $250,000 per business day penalty.\n\n"
        "SECTION 10.4 COMMERCIAL TERMS\n"
        "All invoices are structured under Net 90 extended credit.\n\n"
        "SECTION 14.1 EXECUTIVE SEVERANCE\n"
        "Golden parachute severance packages triggered upon deal closing date.\n\n"
        "SECTION 15.2 RESTRICTIVE COVENANTS\n"
        "Personnel bound by 24-month non-compete covenants."
    )
    manual_txt = st.sidebar.text_area("Contract Text", value=default_text, height=200)
    active_contracts = {"Manual_Excerpt.txt": manual_txt}

st.sidebar.markdown(f"""
<div style="margin-top: 16px; padding: 12px; background-color: #121216; border: 1px solid #24242E; border-radius: 2px;">
    <div style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #FFE600;">VDR Ingestion Summary</div>
    <div style="font-size: 12px; font-weight: 600; color: #FFFFFF; margin-top: 2px; word-break: break-all;">{active_package_name}</div>
    <div style="font-size: 11px; color: #9E9EA8; margin-top: 4px;">Contracts Ingested: {len(active_contracts)}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Swarm Agents")
agent_legal = st.sidebar.checkbox("Legal Workstream Agent", value=True)
agent_fin = st.sidebar.checkbox("Financial Workstream Agent", value=True)
agent_hr = st.sidebar.checkbox("Human Capital Workstream Agent", value=True)

run_audit = st.sidebar.button("EXECUTE DUE DILIGENCE AUDIT")

if "audit_results" not in st.session_state:
    st.session_state["audit_results"] = None
    st.session_state["audited_package"] = None

if run_audit or (st.session_state["audit_results"] is None and active_contracts):
    if not active_contracts:
        st.warning("Please provide or upload contracts to initiate audit.")
    else:
        with st.spinner("Executing LangGraph multi-agent diligence protocol with FAISS vector indexing..."):
            initial_state = VDRAnalysisState(
                vdr_package_name=active_package_name,
                contracts=active_contracts,
                contract_text="\n\n".join(active_contracts.values()),
                risks=[]
            )
            final_state = run_contract_swarm(initial_state)
            
            active_categories = []
            if agent_legal:
                active_categories.append("Legal")
            if agent_fin:
                active_categories.append("Financial")
            if agent_hr:
                active_categories.append("HR")
                
            filtered_risks = [r for r in final_state.risks if r.category in active_categories]
            final_state.risks = filtered_risks
            
            st.session_state["audit_results"] = final_state
            st.session_state["audited_package"] = active_package_name

audit_state = st.session_state.get("audit_results")

if audit_state is not None:
    risks = audit_state.risks
    metrics = audit_state.portfolio_metrics
    high_count = sum(1 for r in risks if r.severity == "High")
    med_count = sum(1 for r in risks if r.severity == "Medium")
    low_count = sum(1 for r in risks if r.severity == "Low")
    
    num_contracts = len(audit_state.contracts) if audit_state.contracts else 1
    status_label = "ACTION REQUIRED" if high_count > 0 else ("MONITORING" if med_count > 0 else "SATISFACTORY")
    status_class = "ey-kpi-card-high" if high_count > 0 else "ey-kpi-card-status"

    st.markdown(f"""
    <div class="ey-kpi-container">
        <div class="ey-kpi-card">
            <div class="ey-kpi-label">VDR Contracts Audited</div>
            <div class="ey-kpi-value">{num_contracts}</div>
            <div class="ey-kpi-subtext">Multi-contract corporate archive</div>
        </div>
        <div class="ey-kpi-card">
            <div class="ey-kpi-label">Total Liabilities Flagged</div>
            <div class="ey-kpi-value">{len(risks)}</div>
            <div class="ey-kpi-subtext">Indexed via FAISS vector store</div>
        </div>
        <div class="ey-kpi-card ey-kpi-card-high">
            <div class="ey-kpi-label">High Severity Exposure</div>
            <div class="ey-kpi-value" style="color: #DC2626;">{high_count}</div>
            <div class="ey-kpi-subtext">Deal structuring remediation</div>
        </div>
        <div class="ey-kpi-card {status_class}">
            <div class="ey-kpi-label">Diligence Clearance Status</div>
            <div class="ey-kpi-value" style="font-size: 20px; font-weight: 700; padding-top: 4px; color: #FFE600;">{status_label}</div>
            <div class="ey-kpi-subtext">EY Transaction Guidelines</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ey-summary-box">
        <div class="ey-summary-title">M&A Partner Executive Summary</div>
        <p class="ey-summary-text">{audit_state.executive_summary}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "PORTFOLIO DASHBOARD",
        "UNIFIED RISK MATRIX",
        "WORKSTREAM ANALYSIS",
        "CONTRACT CLAUSES",
        "M&A PARTNER MEMO & EXPORT"
    ])

    with tab1:
        st.markdown('<div class="ey-section-title">Portfolio Distribution and Contract Breakdown</div>', unsafe_allow_html=True)
        col_c1, col_c2 = st.columns([1, 1])
        
        with col_c1:
            contract_counts = metrics.get("contract_breakdown", {})
            if not contract_counts and audit_state.contracts:
                for c in audit_state.contracts.keys():
                    contract_counts[c] = sum(1 for r in risks if r.contract_name == c)
                    
            df_contracts = pd.DataFrame(
                [{"Contract Document": k, "Liabilities Identified": v} for k, v in contract_counts.items()]
            )
            st.dataframe(df_contracts, hide_index=True, width="stretch")

        with col_c2:
            workstream_counts = {
                "Legal Workstream": sum(1 for r in risks if r.category == "Legal"),
                "Financial Workstream": sum(1 for r in risks if r.category == "Financial"),
                "Human Capital Workstream": sum(1 for r in risks if r.category == "HR")
            }
            df_ws = pd.DataFrame(list(workstream_counts.items()), columns=["Workstream", "Flagged Liabilities"])
            st.dataframe(df_ws, hide_index=True, width="stretch")

        st.markdown('<div class="ey-section-title">Critical High Severity Liabilities</div>', unsafe_allow_html=True)
        priority_risks = [r for r in risks if r.severity == "High"]
        if priority_risks:
            for idx, pr in enumerate(priority_risks, 1):
                st.markdown(f"""
                <div class="ey-finding-card" style="border-left: 4px solid #DC2626;">
                    <div style="margin-bottom: 6px;">
                        <span class="ey-badge ey-badge-high">HIGH SEVERITY</span>
                        <span class="ey-badge ey-badge-workstream">{pr.category.upper()} WORKSTREAM</span>
                        <span style="font-size: 11px; font-weight: 600; color: #9E9EA8;">Document: {pr.contract_name}</span>
                    </div>
                    <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin: 4px 0;">{pr.clause_reference}</div>
                    <div style="font-size: 13px; color: #D4D4D8; margin: 6px 0;"><strong>Identified Liability:</strong> {pr.description}</div>
                    <div style="font-size: 13px; color: #FFFFFF; background-color: #17171C; padding: 10px 14px; border: 1px solid #24242E; border-left: 3px solid #FFE600; border-radius: 2px;">
                        <strong>Recommended EY Action:</strong> {pr.mitigation}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No high severity liabilities detected across the audited portfolio.")

    with tab2:
        st.markdown('<div class="ey-section-title">Unified Multi-Contract Risk Matrix</div>', unsafe_allow_html=True)
        
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            contract_options = ["All Contracts"] + list(audit_state.contracts.keys())
            c_filter = st.selectbox("Filter by Contract Document", contract_options)
        with col_f2:
            ws_filter = st.selectbox("Filter by Workstream", ["All Workstreams", "Legal", "Financial", "HR"])
        with col_f3:
            s_filter = st.selectbox("Filter by Severity", ["All Severities", "High", "Medium", "Low"])
            
        display_risks = risks
        if c_filter != "All Contracts":
            display_risks = [r for r in display_risks if r.contract_name == c_filter]
        if ws_filter != "All Workstreams":
            display_risks = [r for r in display_risks if r.category == ws_filter]
        if s_filter != "All Severities":
            display_risks = [r for r in display_risks if r.severity == s_filter]

        if display_risks:
            table_rows = []
            for r in display_risks:
                sev_badge_class = "ey-badge-high" if r.severity == "High" else ("ey-badge-medium" if r.severity == "Medium" else "ey-badge-low")
                row_html = f"""
                <tr>
                    <td style="font-weight: 600; font-size: 12px; color: #FFE600;">{r.contract_name}</td>
                    <td style="font-weight: 600; white-space: nowrap; color: #FFFFFF;">{r.category}</td>
                    <td><span class="ey-badge {sev_badge_class}">{r.severity.upper()}</span></td>
                    <td style="font-weight: 600; color: #FFFFFF;">{r.clause_reference}</td>
                    <td>{r.description}</td>
                    <td style="background-color: #17171C; color: #FFFFFF;">{r.mitigation}</td>
                </tr>
                """
                table_rows.append(row_html)
                
            table_html = f"""
            <table class="ey-table">
                <thead>
                    <tr>
                        <th style="width: 18%;">Contract Document</th>
                        <th style="width: 10%;">Workstream</th>
                        <th style="width: 8%;">Severity</th>
                        <th style="width: 20%;">Clause Reference</th>
                        <th style="width: 22%;">Liability Description</th>
                        <th style="width: 22%;">EY Recommended Mitigation</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("No liabilities match the specified filter criteria.")

    with tab3:
        st.markdown('<div class="ey-section-title">Specialized Workstream Findings</div>', unsafe_allow_html=True)
        workstreams = ["Legal", "Financial", "HR"]
        ws_labels = {
            "Legal": "Legal and Regulatory Workstream",
            "Financial": "Financial, Treasury, and Commercial Workstream",
            "HR": "Human Capital and Executive Compensation Workstream"
        }
        
        for ws in workstreams:
            ws_risks = [r for r in risks if r.category == ws]
            st.markdown(f"#### {ws_labels[ws]}")
            if ws_risks:
                for idx, r in enumerate(ws_risks, 1):
                    sev_class = "ey-badge-high" if r.severity == "High" else ("ey-badge-medium" if r.severity == "Medium" else "ey-badge-low")
                    st.markdown(f"""
                    <div class="ey-finding-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 13px; font-weight: 700; color: #FFFFFF;">Finding {idx:02d}: {r.clause_reference}</span>
                            <span class="ey-badge {sev_class}">{r.severity.upper()}</span>
                        </div>
                        <div style="font-size: 11px; color: #9E9EA8; margin-bottom: 6px;">Document: {r.contract_name}</div>
                        <p style="font-size: 13px; color: #D4D4D8; margin: 4px 0 8px 0;">{r.description}</p>
                        <div style="font-size: 12px; color: #FFFFFF; background-color: #17171C; padding: 8px 12px; border-left: 3px solid #FFE600;">
                            <strong>Advisory Action:</strong> {r.mitigation}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='font-size: 13px; color: #71717A;'>No liabilities detected under {ws} workstream.</p>", unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="ey-section-title">Audited Contract Clause Repository</div>', unsafe_allow_html=True)
        if audit_state.contracts:
            selected_inspect_doc = st.selectbox("Select Contract Document to Inspect", list(audit_state.contracts.keys()))
            inspected_text = audit_state.contracts.get(selected_inspect_doc, "")
            st.markdown(f"**Document Name:** {selected_inspect_doc}")
            st.markdown(f"**Character Count:** {len(inspected_text)} | **Word Count:** {len(inspected_text.split())}")
            st.text_area(
                "Extracted Clauses",
                value=inspected_text,
                height=360,
                disabled=True,
                label_visibility="collapsed"
            )
        else:
            st.text_area("Contract Clauses Excerpt", value=audit_state.contract_text, height=360, disabled=True)

    with tab5:
        st.markdown('<div class="ey-section-title">M&A Partner Deliverables & Formal Memorandum</div>', unsafe_allow_html=True)
        
        memo_lines = [
            "================================================================================",
            "ERNST & YOUNG STRATEGY AND TRANSACTIONS - M&A DUE DILIGENCE EXECUTIVE MEMO",
            "================================================================================",
            f"VDR PACKAGE: {st.session_state.get('audited_package', 'VDR Archive')}",
            f"DATE OF AUDIT: 2026-11-12",
            f"ENGAGEMENT: Project Horizon Confirmatory Due Diligence",
            f"TOTAL CONTRACTS AUDITED: {num_contracts}",
            f"PORTFOLIO CLEARANCE STATUS: {status_label}",
            "--------------------------------------------------------------------------------",
            "EXECUTIVE SUMMARY FOR M&A PARTNERS:",
            audit_state.executive_summary,
            "--------------------------------------------------------------------------------",
            "PORTFOLIO PERFORMANCE METRICS:",
            f"Total Liabilities Flagged : {len(risks)}",
            f"High Severity Exposure    : {high_count}",
            f"Medium Severity Items     : {med_count}",
            f"Low Severity Items        : {low_count}",
            "--------------------------------------------------------------------------------",
            "UNIFIED RISK MATRIX FINDINGS ACROSS VDR CONTRACTS:",
        ]
        
        for idx, r in enumerate(risks, 1):
            memo_lines.extend([
                f"\n[{idx:02d}] DOCUMENT: {r.contract_name}",
                f"     WORKSTREAM        : {r.category.upper()} | SEVERITY: {r.severity.upper()}",
                f"     CLAUSE REFERENCE  : {r.clause_reference}",
                f"     LIABILITY SUMMARY : {r.description}",
                f"     RECOMMENDED ACTION: {r.mitigation}"
            ])
            
        memo_lines.extend([
            "\n================================================================================",
            "END OF MEMORANDUM - EY CONFIDENTIAL WORK PRODUCT FOR M&A PARTNERS",
            "================================================================================"
        ])
        
        full_memo_text = "\n".join(memo_lines)
        st.text_area("M&A Partner Memo Preview", value=full_memo_text, height=280, disabled=True)
        
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            st.download_button(
                label="DOWNLOAD PARTNER MEMO (.TXT)",
                data=full_memo_text,
                file_name="EY_MA_Partner_Due_Diligence_Memo.txt",
                mime="text/plain"
            )
        with col_d2:
            json_export = json.dumps({
                "engagement": "Project Horizon Due Diligence",
                "vdr_package": st.session_state.get("audited_package", "VDR Archive"),
                "status": status_label,
                "executive_summary": audit_state.executive_summary,
                "portfolio_metrics": metrics,
                "risk_matrix": [r.model_dump() for r in risks]
            }, indent=2)
            st.download_button(
                label="DOWNLOAD UNIFIED RISK MATRIX (.JSON)",
                data=json_export,
                file_name="EY_Unified_VDR_Risk_Matrix.json",
                mime="application/json"
            )
else:
    st.info("Select or upload a VDR contract package and click 'EXECUTE DUE DILIGENCE AUDIT'.")
