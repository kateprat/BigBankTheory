from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from utils import *

def compToPassport(pdf_path, passport_path, docx_path):
    fields = extract_pdf(pdf_path)

    pdf_data = {
        "first_name": fields.get("account_holder_name").upper(),
        "last_name": fields.get("account_holder_surname").upper(),
        "passport_number": fields.get("passport_number"),
    }

    passport_text = extract_png(passport_path)

    #compare info in the pdf to the information present in the passport text 
    
    mismatches = []

    for field in pdf_data.keys() :
        value = pdf_data[field]
        if not value :
            mismatches.append(f"{field} is missing in PDF")
        elif value.lower() not in passport_text:
            mismatches.append(f"mismatch for {field} : {value}")

    print("here is the passport text to compare: ", f"{passport_text}")
    return mismatches


def compProfileAccount(pdf_path, docx_path): 
    pdf_data = extract_pdf(pdf_path)
    docx_data = parse_docx(docx_path)

    print(f"pdf : {pdf_data.keys()}")
    print(f"docx: {docx_data.keys()}")

    # fields to compare 
    field_ids = [("account_holder_name","first_middle_names"), 
                 ("account_holder_surname","last_name"), 
                 ("passport_number","id_passport_number"), 
                 ("country","country_of_domicile"), 
                 ("phone_number","telephone"), 
                 ("email","email")]
    
    mismatches = [0 if pdf_data.get(id1) == docx_data.get(id2) else 1 for id1, id2 in field_ids]

    # fields that should be in address
    addr = ["building_number", "postal_code", "city", "street_name"]
    for a in addr : 
        if pdf_data.get(a) not in docx_data.get("address"): 
            mismatches.append(1)
        else:  mismatches.append(0)

    return mismatches




if __name__ == "__main__":
    # Example usage compare pdf against passport 
    pdf_path = "client_data/client_502/account.pdf"
    passport_path = "client_data/client_502/passport.png"
    docx_path = "client_data/client_502/profile.docx"

    # errors = compToPassport(pdf_path, passport_path, docx_path )

    # if not errors:
    #     print("All fields are present and match passport content.")
    # else:
    #     print("Mismatches found:")
    #     for error in errors:
    #         print(" -", error)

    print(compProfileAccount(pdf_path=pdf_path, docx_path=docx_path))
