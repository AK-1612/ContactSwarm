import os
import zipfile
from pypdf import PdfReader

def create_simple_pdf(path: str, title: str, paragraphs: list[str]):
    stream_lines = ["BT", "/F1 11 Tf", "40 750 Td", "14 TL"]
    for para in paragraphs:
        sanitized = para.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_lines.append(f"({sanitized}) \'")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("latin-1")
    
    parts = []
    parts.append(b"%PDF-1.4\n")
    offsets = []
    
    def add_obj(content: bytes):
        offsets.append(sum(len(p) for p in parts))
        num = len(offsets)
        parts.append(f"{num} 0 obj\n".encode("ascii") + content + b"\nendobj\n")
        return num

    add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    add_obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add_obj(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    add_obj(f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream")
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    
    xref_offset = sum(len(p) for p in parts)
    parts.append(f"xref\n0 {len(offsets) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for off in offsets:
        parts.append(f"{off:010d} 00000 n \n".encode("ascii"))
        
    parts.append(f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"".join(parts))

def generate_sample_contracts():
    sample1_paras = [
        "CONFIDENTIAL - MERGER AND ACQUISITION AGREEMENT",
        "PROJECT HORIZON / TARGET ACQUISITION TRANSACTION",
        "DATE: OCTOBER 24 2026",
        " ",
        "SECTION 4.1 INDEMNIFICATION AND HOLD HARMLESS",
        "Target Corp agrees to fully indemnify and hold harmless the Buyer from all liabilities.",
        "Buyer agrees to unlimited liability for environmental and historical litigation claims.",
        " ",
        "SECTION 7.3 CHANGE OF CONTROL",
        "Any Change of Control requires unanimous prior written consent from minority debt holders.",
        "Failure to obtain consent within 30 days triggers an automatic debt acceleration event.",
        " ",
        "SECTION 9.2 LIQUIDATED DAMAGES AND PENALTY",
        "In the event of integration delay exceeding 45 days, Buyer shall pay a penalty of $500,000 per week.",
        "Total liquidated damages are uncapped under this schedule.",
        " ",
        "SECTION 10.5 PAYMENT TERMS",
        "Vendor invoices are subject to Net 90 payment terms from receipt of undisputed statement.",
        " ",
        "SECTION 14.2 EXECUTIVE RETENTION AND SEVERANCE",
        "Upon closing, Tier 1 executives are entitled to an immediate golden parachute severance package.",
        "Each C-level executive receives 3x annual base salary plus accelerated equity vesting.",
        " ",
        "SECTION 15.1 RESTRICTIVE COVENANTS",
        "Key engineering personnel are bound by a 36-month non-compete restrictive covenant."
    ]
    
    sample2_paras = [
        "CONFIDENTIAL - VENDOR MASTER SERVICES AGREEMENT",
        "PROJECT TITAN / ENTERPRISE INFRASTRUCTURE PARTNERSHIP",
        "DATE: NOVEMBER 02 2026",
        " ",
        "SECTION 5.2 LIMITATION OF LIABILITY AND INDEMNIFICATION",
        "Vendor requires mutual indemnification for all third party intellectual property claims.",
        " ",
        "SECTION 8.1 COMMERCIAL TERMS",
        "Client payment obligations are structured on Net 120 credit terms.",
        "Late payments incur a penalty fee of 2.5 percent compounding monthly.",
        "Minimum commitment requires client to maintain annual spend of at least $1,200,000.",
        " ",
        "SECTION 11.4 RESTRICTIVE COVENANTS",
        "Client shall not solicit or hire any vendor engineer under the non-compete clause for 24 months."
    ]

    sample3_paras = [
        "CONFIDENTIAL - EXECUTIVE EMPLOYMENT AND RETENTION AGREEMENT",
        "PROJECT APEX / KEY EXECUTIVE RETENTION SCHEDULE",
        "DATE: NOVEMBER 10 2026",
        " ",
        "SECTION 3.2 CHANGE OF CONTROL TRANSACTIONS",
        "Upon any change of control event, executive receives an automatic retention bonus of $750,000.",
        "Executive benefits include accelerated vesting of all outstanding stock options.",
        " ",
        "SECTION 6.1 SEVERANCE ENTITLEMENT",
        "Voluntary resignation within 180 days post-merger triggers full golden parachute severance payout.",
        " ",
        "SECTION 8.4 RESTRICTIVE COVENANTS",
        "Executive agrees to 12-month post-employment non-compete and non-solicitation restrictions."
    ]

    p1 = "vdr_docs/Project_Horizon_Merger_Agreement.pdf"
    p2 = "vdr_docs/Vendor_Master_Services_Agreement.pdf"
    p3 = "vdr_docs/Executive_Retention_Agreement.pdf"

    create_simple_pdf(p1, "Project Horizon Merger Agreement", sample1_paras)
    create_simple_pdf(p2, "Vendor Master Services Agreement", sample2_paras)
    create_simple_pdf(p3, "Executive Retention Agreement", sample3_paras)

    # Build the VDR Corporate Contracts ZIP package
    zip_path = "vdr_docs/VDR_Corporate_Contracts_Package.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(p1, arcname=os.path.basename(p1))
        z.write(p2, arcname=os.path.basename(p2))
        z.write(p3, arcname=os.path.basename(p3))

    print(f"Sample contracts and VDR ZIP package created: {zip_path}")

if __name__ == "__main__":
    generate_sample_contracts()
