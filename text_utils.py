import pickle
from PyPDF2 import PdfReader
import docx
from io import BytesIO

class TextUtils:
    def __init__(self):
        pass

    def extract_text(self, byte_stream, file_extension):
        if file_extension.lower() == '.pdf':
            return self._extract_text_from_pdf(byte_stream)
        elif file_extension.lower() == '.docx':
            return self._extract_text_from_docx(byte_stream)
        elif file_extension.lower() == '.txt':
            return self._extract_text_from_txt(byte_stream)
        else:
            raise ValueError("Unsupported file type: {}".format(file_extension))

    def _extract_text_from_pdf(self, byte_stream):
        text = ""
        reader = PdfReader(byte_stream)
        for page in reader.pages:
            text += page.extract_text()
        return text

    def _extract_text_from_docx(self, byte_stream):
        byte_stream.seek(0)
        doc = docx.Document(byte_stream)
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_text_from_txt(self, byte_stream):
        byte_stream.seek(0)
        return byte_stream.read().decode('utf-8')

    def chunk_text(self, text, chunk_size=1000, overlap=100):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
    
    def pickle_data(self, data):
        return pickle.dumps(data)

    def unpickle_data(self, pickled_data):
        return pickle.loads(pickled_data)