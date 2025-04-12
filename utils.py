from PyPDF2 import PdfReader
from docx import Document
import pytesseract
from PIL import Image
import os
import base64


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

def extract_png(passport_path): 
    image = Image.open(passport_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text


def save_passport_image(json_data, output_dir, filename="passport.png"):
    if "passport" not in json_data:
        raise ValueError("Field 'passport' not found in the provided JSON data.")

    os.makedirs(output_dir, exist_ok=True)
    image_data = base64.b64decode(json_data["passport"])
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(image_data)

    return filepath

def save_docx_file(json_data, output_dir, filename="profile.docx"):
    if "profile" not in json_data:
        raise ValueError("Field 'profile' not found in the provided JSON data.")

    os.makedirs(output_dir, exist_ok=True)

    docx_data = base64.b64decode(json_data["profile"])
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(docx_data)

    return filepath

def save_pdf_file(json_data, output_dir, filename="account.pdf"):
    if "account" not in json_data:
        raise ValueError("Field 'account' not found in the provided JSON data.")

    os.makedirs(output_dir, exist_ok=True)

    pdf_data = base64.b64decode(json_data["account"])
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(pdf_data)

    return filepath

def save_description_txt(json_data, output_dir, filename="description.txt"):
    if "description" not in json_data:
        raise ValueError("Field 'description' not found in the provided JSON data.")

    os.makedirs(output_dir, exist_ok=True)

    txt_data = base64.b64decode(json_data["description"])
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(txt_data)

    return filepath