from matcher.parser import extract_text, ParsingError
import pytest

class FakeUploadedFile:
    """Mimics Streamlit's UploadedFile interface for testing without Streamlit running."""
    def __init__(self, path):
        self.name = path
        self._file = open(path, "rb")

    def __getattr__(self, attr):
        return getattr(self._file, attr)

def test_extract_text_from_docx():
    fake_file = FakeUploadedFile("tests/documents/sample_resume.docx")
    text = extract_text(fake_file)
    assert len(text) > 0

def text_unsupported_file_type_raises():
    with pytest.raises(ParsingError):
        extract_text(FakeUploadedFile("tests/documents/sample_resume.txt"))
