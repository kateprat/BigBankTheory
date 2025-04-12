from PyPDF2 import PdfReader
from docx import Document


def extract_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    return {k : v.get('/V', None) for k,v in fields.items()}

def parse_docx(path) :
    doc = Document(path)
    table = doc.tables[1]
    data = {
        "last_name": table.rows[0].cells[2].text.strip(),
        "first_middle_names": table.rows[1].cells[2].text.strip(),
        "address": table.rows[2].cells[2].text.strip(),
        "country_of_domicile": table.rows[3].cells[2].text.strip(),
        "date_of_birth": table.rows[4].cells[2].text.strip(),
        "nationality": table.rows[5].cells[2].text.strip(),
        "id_passport_number": table.rows[6].cells[2].text.strip(),
        "id_type": table.rows[7].cells[2].text.strip(),
        "id_issue_date": table.rows[8].cells[2].text.strip(),
        "id_expiry_date": table.rows[9].cells[2].text.strip(),
    }

    gender_cell = table.rows[10].cells[2].text
    if '☒ Male' in gender_cell:
        data["gender"] = "male"
    elif '☒ Female' in gender_cell:
        data["gender"] = "female"
    else:
        data["gender"] = "unknown"
        
    table = doc.tables[3]
    data.update( {
        "telephone": "".join(table.rows[0].cells[2].text.strip().split()[1:]),
        "email": table.rows[2].cells[2].text.strip().split()[1],
    })
    return data