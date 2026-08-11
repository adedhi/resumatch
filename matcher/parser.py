from docx import Document
import pdfplumber

class ParsingError(Exception):
    """Raised when a resume file can't be read or contains no usable text."""
    pass

def extract_text_from_pdf(file) -> str:
    try:
        text_parts = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        raise ParsingError(f"Could not read PDF file: {e}")

def extract_text_from_docx(file) -> str:
    try:
        doc = Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)
    except Exception as e:
        raise ParsingError(f"Could not read docx file: {e}")

def extract_text(uploaded_file) -> str:
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)
    else:
        raise ParsingError(f"Unsupported file type: {filename}")

    if not text.strip():
        raise ParsingError(
            "No text could be extracted from this file. "
            "It may be a scanned image rather than selectable text."
        )

    if len(text.strip()) < 50:
        raise ParsingError(
            "Very little text could be extracted from this file. "
            "It may be image-based or have a complex layout that isn't parsing well."
        )

    return text
