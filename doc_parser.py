import os
import zipfile
import io
from typing import Dict, List, Tuple
from pypdf import PdfReader

class DocumentParser:
    def __init__(self):
        self.azure_endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
        self.azure_key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")

    def is_azure_configured(self) -> bool:
        return bool(self.azure_endpoint and self.azure_key)

    def parse_pdf_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> str:
        # If Azure Document Intelligence credentials are provided, cloud OCR can be invoked
        if self.is_azure_configured():
            try:
                azure_text = self._parse_with_azure(pdf_bytes)
                if azure_text:
                    return azure_text
            except Exception:
                pass  # Fall back gracefully to local engine
                
        # Local deterministic PyPDF extraction engine
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t.strip())
        return "\n\n".join(pages_text)

    def _parse_with_azure(self, pdf_bytes: bytes) -> str:
        # Placeholder for Azure Document Intelligence REST API
        # When cloud credentials are live, this issues the analyze document request
        return ""

    def parse_file(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        lower_name = filepath.lower()
        if lower_name.endswith(".pdf"):
            with open(filepath, "rb") as f:
                return self.parse_pdf_bytes(f.read(), os.path.basename(filepath))
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def parse_vdr_zip(self, zip_source) -> Dict[str, str]:
        """
        Ingests a zip file of corporate contracts (path or bytes/BytesIO)
        and outputs a dictionary mapping filename to extracted text.
        """
        contracts = {}
        
        if isinstance(zip_source, (str, os.PathLike)):
            z = zipfile.ZipFile(zip_source, "r")
        else:
            if hasattr(zip_source, "read"):
                zip_source = zip_source.read()
            z = zipfile.ZipFile(io.BytesIO(zip_source), "r")

        with z:
            for item in z.namelist():
                # Skip directories and hidden/metadata files
                if item.endswith("/") or item.startswith("__MACOSX/") or os.path.basename(item).startswith("."):
                    continue
                    
                basename = os.path.basename(item)
                lower_name = basename.lower()
                
                if lower_name.endswith(".pdf"):
                    pdf_bytes = z.read(item)
                    extracted = self.parse_pdf_bytes(pdf_bytes, basename)
                    if extracted.strip():
                        contracts[basename] = extracted
                elif lower_name.endswith((".txt", ".md", ".json", ".csv")):
                    text_bytes = z.read(item)
                    extracted = text_bytes.decode("utf-8", errors="ignore")
                    if extracted.strip():
                        contracts[basename] = extracted

        return contracts

