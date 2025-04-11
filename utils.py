from PyPDF2 import PdfReader


def extract_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    return {k : v.get('/V', None) for k,v in fields.items()}

