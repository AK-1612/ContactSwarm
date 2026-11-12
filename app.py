import os
import io
import json
import pandas as pd
import streamlit as st

from state import VDRAnalysisState
from doc_parser import DocumentParser
from orchestrator import run_contract_swarm

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
    page_title="ContractSwarm - EY Strategy and Transactions",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: #09090B !important;
    color: #F4F4F5 !important;
}

/* Remove all top padding */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}
.main .block-container,
div[data-testid="stMainBlockContainer"],
.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
}
div[data-testid="stSidebarHeader"],
div[data-testid="stSidebarHeader"] > * {
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="stSidebarContent"] {
    padding-top: 2rem !important;
    background-color: #0D0D10 !important;
}
section[data-testid="stSidebar"] {
    background-color: #0D0D10 !important;
    border-right: 1px solid #1F1F28 !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #A1A1AA !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h2 {
    color: #FFFFFF !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
}

/* Button */
div.stButton > button {
    background-color: #FFE600 !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border-radius: 2px !important;
    border: none !important;
    padding: 11px 20px !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
    width: 100% !important;
    margin-top: 8px !important;
}
div.stButton > button:hover {
    background-color: #FFF176 !important;
}

/* Tabs */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #52525B !important;
    padding: 10px 16px !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFE600 !important;
    border-bottom: 2px solid #FFE600 !important;
}
div[data-testid="stTabs"] [data-testid="stTabsContent"] {
    padding-top: 1.5rem !important;
}

/* Selectbox, radio */
div[data-baseweb="select"] > div {
    background-color: #111115 !important;
    border-color: #27272A !important;
    color: #F4F4F5 !important;
}
div[data-baseweb="radio"] label span {
    color: #A1A1AA !important;
}
textarea {
    background-color: #111115 !important;
    border-color: #27272A !important;
    color: #D4D4D8 !important;
    font-size: 12px !important;
}
div[data-testid="stFileUploader"] {
    background-color: #111115 !important;
    border: 1px dashed #27272A !important;
    border-radius: 4px !important;
}

/* Download buttons */
div.stDownloadButton > button {
    background-color: transparent !important;
    color: #FFE600 !important;
    border: 1px solid #FFE600 !important;
    font-weight: 600 !important;
    border-radius: 2px !important;
    padding: 8px 16px !important;
    font-size: 11px !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    width: 100% !important;
}
div.stDownloadButton > button:hover {
    background-color: #FFE600 !important;
    color: #000000 !important;
}

/* Spinner */
div[data-testid="stSpinner"] p { color: #A1A1AA !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── HEADER ───────────────────────────
st.markdown('<div style="height:5px;background:#FFE600;margin-bottom:1.5rem;"></div>', unsafe_allow_html=True)

st.markdown("""
<div style="
    background:#111115;
    border-left:4px solid #FFE600;
    border:1px solid #1F1F28;
    border-left:4px solid #FFE600;
    padding:24px 28px;
    border-radius:2px;
    margin-bottom:2rem;
">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2.5px;color:#FFE600;margin-bottom:8px;">
        EY Strategy and Transactions &nbsp;|&nbsp; M&A Due Diligence
    </div>
    <div style="font-size:22px;font-weight:700;color:#FFFFFF;letter-spacing:-0.3px;margin-bottom:4px;">
        ContractSwarm Autonomous Diligence Fabric
    </div>
    <div style="font-size:13px;color:#71717A;font-weight:400;line-height:1.5;">
        Multi-agent cognitive orchestration for virtual data room liability audits, contractual risk indexing, and deal governance.
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────── SIDEBAR ───────────────────────────
parser = DocumentParser()

st.sidebar.markdown("""
<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #1F1F28;">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#FFE600;margin-bottom:6px;">Engagement</div>
    <div style="font-size:12px;color:#71717A;">Project Horizon Due Diligence</div>
    <div style="font-size:12px;color:#71717A;">EY Strategy and Transactions</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Contract Source")

vdr_dir = "vdr_docs"
sample_zips = sorted([f for f in os.listdir(vdr_dir) if f.endswith(".zip")]) if os.path.exists(vdr_dir) else []
sample_pdfs = sorted([f for f in os.listdir(vdr_dir) if f.endswith(".pdf")]) if os.path.exists(vdr_dir) else []

input_mode = st.sidebar.radio(
    "source",
    ["VDR ZIP Package", "Single PDF", "Paste Text"],
    label_visibility="collapsed"
)

# Document selection — only load bytes, never auto-run
contract_ready = False
active_contracts: dict[str, str] = {}
active_package_name = ""

if input_mode == "VDR ZIP Package":
    source = st.sidebar.radio(
        "zip_source",
        ["Use preloaded sample", "Upload your own"],
        label_visibility="collapsed"
    )
    if source == "Use preloaded sample":
        if sample_zips:
            chosen = st.sidebar.selectbox("Select ZIP", sample_zips)
            active_package_name = chosen
            contract_ready = True
        else:
            st.sidebar.caption("No sample ZIPs found.")
    else:
        up = st.sidebar.file_uploader("Upload ZIP archive", type=["zip"])
        if up:
            active_package_name = up.name
            # Store raw bytes in session state to avoid re-read on rerun
            st.session_state["_zip_bytes"] = up.read()
            contract_ready = True

elif input_mode == "Single PDF":
    source = st.sidebar.radio(
        "pdf_source",
        ["Use preloaded sample", "Upload your own"],
        label_visibility="collapsed"
    )
    if source == "Use preloaded sample":
        if sample_pdfs:
            chosen = st.sidebar.selectbox("Select PDF", sample_pdfs)
            active_package_name = chosen
            contract_ready = True
        else:
            st.sidebar.caption("No sample PDFs found.")
    else:
        up = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
        if up:
            active_package_name = up.name
            st.session_state["_pdf_bytes"] = up.read()
            st.session_state["_pdf_name"] = up.name
            contract_ready = True

elif input_mode == "Paste Text":
    pasted = st.sidebar.text_area(
        "Contract text",
        placeholder="Paste contract clauses here...",
        height=180
    )
    if pasted.strip():
        active_package_name = "Pasted Contract"
        contract_ready = True

st.sidebar.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)
st.sidebar.markdown("### Swarm Agents")
agent_legal = st.sidebar.checkbox("Legal Workstream", value=True)
agent_fin   = st.sidebar.checkbox("Financial Workstream", value=True)
agent_hr    = st.sidebar.checkbox("Human Capital Workstream", value=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

run_btn = st.sidebar.button("EXECUTE AUDIT", disabled=(not contract_ready))


# ─────────────────────────── RUN AUDIT ───────────────────────────
if run_btn and contract_ready:
    # Build contract map only on explicit button press
    with st.spinner("Running multi-agent diligence protocol..."):
        if input_mode == "VDR ZIP Package":
            if source == "Use preloaded sample":
                active_contracts = parser.parse_vdr_zip(os.path.join(vdr_dir, chosen))
            else:
                active_contracts = parser.parse_vdr_zip(io.BytesIO(st.session_state.get("_zip_bytes", b"")))

        elif input_mode == "Single PDF":
            if source == "Use preloaded sample":
                txt = parser.parse_file(os.path.join(vdr_dir, chosen))
                active_contracts = {chosen: txt}
            else:
                b = st.session_state.get("_pdf_bytes", b"")
                n = st.session_state.get("_pdf_name", "contract.pdf")
                active_contracts = {n: parser.parse_pdf_bytes(b, n)}

        elif input_mode == "Paste Text":
            active_contracts = {"Pasted_Contract.txt": pasted}

        # Build state and run swarm
        initial = VDRAnalysisState(
            vdr_package_name=active_package_name,
            contracts=active_contracts,
            contract_text="\n\n".join(active_contracts.values()),
        )
        final = run_contract_swarm(initial)

        # Apply agent toggles
        allowed = []
        if agent_legal: allowed.append("Legal")
        if agent_fin:   allowed.append("Financial")
        if agent_hr:    allowed.append("HR")
        final.risks = [r for r in final.risks if r.category in allowed]

        st.session_state["results"] = final
        st.session_state["package_name"] = active_package_name


# ─────────────────────────── EMPTY STATE ───────────────────────────
if "results" not in st.session_state:
    st.markdown("""
<div style="
    margin-top:3rem;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    gap:12px;
">
    <div style="
        width:56px;height:56px;
        border:2px solid #27272A;
        border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        margin:0 auto 8px;
    ">
        <div style="width:24px;height:2px;background:#FFE600;"></div>
    </div>
    <div style="font-size:18px;font-weight:700;color:#FFFFFF;">
        No audit executed yet
    </div>
    <div style="font-size:13px;color:#71717A;max-width:400px;line-height:1.6;">
        Select a contract source from the sidebar and click
        <span style="color:#FFE600;font-weight:600;">EXECUTE AUDIT</span>
        to initiate the multi-agent due diligence protocol.
    </div>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────── RESULTS ───────────────────────────
state: VDRAnalysisState = st.session_state["results"]
risks   = state.risks
metrics = state.portfolio_metrics

high = sum(1 for r in risks if r.severity == "High")
med  = sum(1 for r in risks if r.severity == "Medium")
low  = sum(1 for r in risks if r.severity == "Low")
n_contracts = len(state.contracts) if state.contracts else 1
status = "ACTION REQUIRED" if high > 0 else ("MONITORING" if med > 0 else "SATISFACTORY")
status_color = "#DC2626" if high > 0 else ("#F59E0B" if med > 0 else "#22C55E")


# ── KPI Row ──
def kpi_card(label, value, sub, accent="#3F3F46"):
    return f"""
<div style="
    flex:1;
    background:#111115;
    border:1px solid #1F1F28;
    border-top:2px solid {accent};
    border-radius:2px;
    padding:20px 20px 16px;
">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#71717A;margin-bottom:10px;">{label}</div>
    <div style="font-size:30px;font-weight:700;color:#FFFFFF;line-height:1;">{value}</div>
    <div style="font-size:11px;color:#52525B;margin-top:6px;">{sub}</div>
</div>"""

st.markdown(f"""
<div style="display:flex;gap:14px;margin-bottom:1.5rem;">
    {kpi_card("Contracts Audited",    n_contracts, "In this VDR package")}
    {kpi_card("Liabilities Flagged",  len(risks),  "FAISS-indexed clauses")}
    {kpi_card("High Severity",        high,        "Require deal remediation", "#DC2626")}
    {kpi_card("Clearance Status",     status,      "EY Transaction Guidelines", status_color)}
</div>
""", unsafe_allow_html=True)


# ── Executive Summary ──
st.markdown(f"""
<div style="
    background:#111115;
    border:1px solid #1F1F28;
    border-left:3px solid #FFE600;
    border-radius:2px;
    padding:20px 24px;
    margin-bottom:2rem;
">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#FFE600;margin-bottom:10px;">
        M&A Partner Executive Summary
    </div>
    <div style="font-size:14px;color:#D4D4D8;line-height:1.7;">
        {state.executive_summary}
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──
tab1, tab2, tab3, tab4 = st.tabs([
    "RISK MATRIX",
    "WORKSTREAM BREAKDOWN",
    "CONTRACT CLAUSES",
    "EXPORT"
])


# ── Tab 1: Risk Matrix ──
with tab1:
    # Filters
    c1, c2, c3 = st.columns(3)
    with c1:
        f_contract = st.selectbox("Contract", ["All"] + list(state.contracts.keys()), key="f_c")
    with c2:
        f_ws = st.selectbox("Workstream", ["All", "Legal", "Financial", "HR"], key="f_w")
    with c3:
        f_sev = st.selectbox("Severity", ["All", "High", "Medium", "Low"], key="f_s")

    filtered = risks
    if f_contract != "All": filtered = [r for r in filtered if r.contract_name == f_contract]
    if f_ws      != "All": filtered = [r for r in filtered if r.category == f_ws]
    if f_sev     != "All": filtered = [r for r in filtered if r.severity == f_sev]

    st.markdown(f"<div style='font-size:12px;color:#52525B;margin:1rem 0 0.75rem;'>{len(filtered)} finding(s) shown</div>", unsafe_allow_html=True)

    if not filtered:
        st.markdown("<div style='font-size:13px;color:#52525B;padding:1rem 0;'>No findings match the selected filters.</div>", unsafe_allow_html=True)
    else:
        for r in filtered:
            sev_color = "#DC2626" if r.severity == "High" else ("#F59E0B" if r.severity == "Medium" else "#2563EB")
            sev_bg    = "#1C0A0A" if r.severity == "High" else ("#1C1200" if r.severity == "Medium" else "#0A0F1C")
            st.markdown(f"""
<div style="
    background:#111115;
    border:1px solid #1F1F28;
    border-left:3px solid {sev_color};
    border-radius:2px;
    padding:18px 22px;
    margin-bottom:10px;
">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
        <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="
                    font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                    padding:2px 7px;border-radius:2px;
                    background:{sev_bg};color:{sev_color};border:1px solid {sev_color};
                ">{r.severity}</span>
                <span style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;
                    padding:2px 7px;border-radius:2px;background:#18181B;color:#A1A1AA;border:1px solid #27272A;
                ">{r.category}</span>
                <span style="font-size:11px;color:#52525B;">{r.contract_name}</span>
            </div>
            <div style="font-size:14px;font-weight:600;color:#FFFFFF;margin-bottom:6px;">{r.clause_reference}</div>
            <div style="font-size:13px;color:#A1A1AA;line-height:1.5;margin-bottom:10px;">{r.description}</div>
            <div style="font-size:12px;color:#D4D4D8;background:#18181B;border:1px solid #27272A;padding:10px 14px;border-radius:2px;line-height:1.5;">
                <span style="color:#71717A;font-weight:600;">Advisory Action: </span>{r.mitigation}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tab 2: Workstream Breakdown ──
with tab2:
    ws_data = {
        "Legal":     [r for r in risks if r.category == "Legal"],
        "Financial": [r for r in risks if r.category == "Financial"],
        "HR":        [r for r in risks if r.category == "HR"],
    }
    ws_labels = {
        "Legal":     "Legal and Regulatory",
        "Financial": "Financial and Commercial",
        "HR":        "Human Capital and Compensation",
    }

    for ws, ws_risks in ws_data.items():
        h = sum(1 for r in ws_risks if r.severity == "High")
        m = sum(1 for r in ws_risks if r.severity == "Medium")
        l = sum(1 for r in ws_risks if r.severity == "Low")
        total = len(ws_risks)

        st.markdown(f"""
<div style="
    background:#111115;border:1px solid #1F1F28;border-radius:2px;
    padding:16px 20px;margin-bottom:8px;
    display:flex;justify-content:space-between;align-items:center;
">
    <div>
        <div style="font-size:13px;font-weight:600;color:#FFFFFF;">{ws_labels[ws]} Workstream</div>
        <div style="font-size:11px;color:#71717A;margin-top:2px;">{total} finding(s)</div>
    </div>
    <div style="display:flex;gap:8px;">
        <span style="font-size:11px;font-weight:600;padding:3px 9px;border-radius:2px;
            background:#1C0A0A;color:#DC2626;border:1px solid #DC2626;">{h} High</span>
        <span style="font-size:11px;font-weight:600;padding:3px 9px;border-radius:2px;
            background:#1C1200;color:#F59E0B;border:1px solid #F59E0B;">{m} Medium</span>
        <span style="font-size:11px;font-weight:600;padding:3px 9px;border-radius:2px;
            background:#0A0F1C;color:#2563EB;border:1px solid #2563EB;">{l} Low</span>
    </div>
</div>
""", unsafe_allow_html=True)

        if ws_risks:
            with st.expander(f"View {total} {ws} finding(s)", expanded=False):
                for r in ws_risks:
                    sev_color = "#DC2626" if r.severity == "High" else ("#F59E0B" if r.severity == "Medium" else "#2563EB")
                    st.markdown(f"""
<div style="border-left:2px solid {sev_color};padding:10px 14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:4px;">{r.clause_reference}</div>
    <div style="font-size:11px;color:#52525B;margin-bottom:6px;">{r.contract_name}</div>
    <div style="font-size:12px;color:#A1A1AA;line-height:1.5;margin-bottom:6px;">{r.description}</div>
    <div style="font-size:12px;color:#D4D4D8;"><span style="color:#71717A;">Action:</span> {r.mitigation}</div>
</div>
""", unsafe_allow_html=True)
        st.markdown("")


# ── Tab 3: Contract Clauses ──
with tab3:
    if state.contracts:
        doc_sel = st.selectbox("Document", list(state.contracts.keys()))
        txt = state.contracts[doc_sel]
        wc = len(txt.split())
        st.markdown(f"""
<div style="display:flex;gap:24px;margin-bottom:1rem;">
    <div style="font-size:11px;color:#71717A;">Words: <span style="color:#A1A1AA;font-weight:600;">{wc}</span></div>
    <div style="font-size:11px;color:#71717A;">Characters: <span style="color:#A1A1AA;font-weight:600;">{len(txt)}</span></div>
</div>
""", unsafe_allow_html=True)
        st.text_area("", value=txt, height=400, disabled=True, label_visibility="collapsed")
    else:
        st.markdown("<div style='font-size:13px;color:#52525B;'>No contract text available.</div>", unsafe_allow_html=True)


# ── Tab 4: Export ──
with tab4:
    pkg_name = st.session_state.get("package_name", "VDR Package")

    memo_lines = [
        "=" * 80,
        "ERNST & YOUNG STRATEGY AND TRANSACTIONS",
        "M&A DUE DILIGENCE EXECUTIVE MEMORANDUM",
        "=" * 80,
        f"VDR PACKAGE          : {pkg_name}",
        f"DATE OF AUDIT        : 2026-11-12",
        f"ENGAGEMENT           : Project Horizon Confirmatory Due Diligence",
        f"CONTRACTS AUDITED    : {n_contracts}",
        f"CLEARANCE STATUS     : {status}",
        "-" * 80,
        "EXECUTIVE SUMMARY:",
        "",
        state.executive_summary,
        "",
        "-" * 80,
        "PORTFOLIO METRICS:",
        f"  Total Liabilities  : {len(risks)}",
        f"  High Severity      : {high}",
        f"  Medium Severity    : {med}",
        f"  Low Severity       : {low}",
        "",
        "-" * 80,
        "RISK MATRIX:",
        "",
    ]
    for i, r in enumerate(risks, 1):
        memo_lines += [
            f"[{i:02d}] {r.contract_name}",
            f"     Workstream  : {r.category}  |  Severity: {r.severity}",
            f"     Clause      : {r.clause_reference}",
            f"     Liability   : {r.description}",
            f"     Action      : {r.mitigation}",
            "",
        ]
    memo_lines += ["=" * 80, "EY CONFIDENTIAL WORK PRODUCT", "=" * 80]
    memo_text = "\n".join(memo_lines)

    json_out = json.dumps({
        "engagement": "Project Horizon Due Diligence",
        "vdr_package": pkg_name,
        "status": status,
        "executive_summary": state.executive_summary,
        "portfolio_metrics": metrics,
        "risk_matrix": [r.model_dump() for r in risks],
    }, indent=2)

    st.markdown("""
<div style="font-size:13px;color:#71717A;margin-bottom:1.5rem;line-height:1.6;">
    Download the formal audit memorandum or the structured JSON risk matrix
    for integration with deal management workflows.
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
<div style="background:#111115;border:1px solid #1F1F28;border-radius:2px;padding:20px;margin-bottom:12px;">
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#A1A1AA;margin-bottom:4px;">Partner Memo</div>
    <div style="font-size:12px;color:#52525B;">Plain text formal memorandum for M&A partners and senior counsel.</div>
</div>
""", unsafe_allow_html=True)
        st.download_button("DOWNLOAD MEMO (.TXT)", memo_text, "EY_MA_Diligence_Memo.txt", "text/plain")

    with col2:
        st.markdown("""
<div style="background:#111115;border:1px solid #1F1F28;border-radius:2px;padding:20px;margin-bottom:12px;">
    <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#A1A1AA;margin-bottom:4px;">Risk Matrix JSON</div>
    <div style="font-size:12px;color:#52525B;">Structured JSON risk matrix for deal system integration and further analysis.</div>
</div>
""", unsafe_allow_html=True)
        st.download_button("DOWNLOAD MATRIX (.JSON)", json_out, "EY_VDR_Risk_Matrix.json", "application/json")
