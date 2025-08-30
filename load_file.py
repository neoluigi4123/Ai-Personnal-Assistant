import os
import chardet
from docx import Document
from odf.opendocument import load as load_odt
from odf.text import P
from striprtf.striprtf import rtf_to_text
from PyPDF2 import PdfReader

def load_file(file_path: str) -> str:
    """
    Load and return the contents of a text-based file in many formats.

    Supports: .txt, .py, .md, .docx, .odt, .rtf, .pdf (extendable).
    
    Args:
        file_path (str): Absolute path to the file.
    
    Returns:
        str: File contents as a string.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        ValueError: If path is not absolute or unsupported format.
    """
    if not os.path.isabs(file_path):
        raise ValueError("Please provide an absolute file path.")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    # --- Plain text fallback with encoding detection ---
    def read_text_file(path):
        with open(path, "rb") as f:
            raw = f.read()
        detected = chardet.detect(raw)
        encoding = detected["encoding"] or "utf-8"
        return raw.decode(encoding, errors="replace")

    # --- Format handlers ---
    if ext in [".txt", ".py", ".md", ".json", ".csv", ".yaml", ".ini"]:
        return read_text_file(file_path)

    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    elif ext == ".odt":
        doc = load_odt(file_path)
        paragraphs = [t.data for t in doc.getElementsByType(P)]
        return "\n".join(paragraphs)

    elif ext == ".rtf":
        with open(file_path, "r", errors="ignore") as f:
            return rtf_to_text(f.read())

    elif ext == ".pdf":
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text.append(extracted)
        return "\n".join(text)

    else:
        raise ValueError(f"Unsupported file format: {ext}")
