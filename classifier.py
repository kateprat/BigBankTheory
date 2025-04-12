import utils
import os
from llm_compare import check_consistency_with_groq

class Classifier:
    def __init__(self) :
        pass

    def classify(self, client_path : str) :
        
        self.pdf_path = os.path.join(client_path, "account.pdf")
        self.passport_path = os.path.join(client_path, "passport.png")
        self.docx_path = os.path.join(client_path, "profile.docx")
        self.description_path = os.path.join(client_path, "description.txt")
        
        # passport_pass = self._compToPassport()
        docx_pdf_pass = self._check_docx_pdf()
        # return self._llm_compare()
    
    
        return docx_pdf_pass
        
        
    
    def _llm_compare(self) :
        pdf_data = utils.extract_pdf(self.pdf_path)
        docx_data = utils.parse_docx(self.docx_path)
        ans = check_consistency_with_groq(docx_data, pdf_data)
        print(ans)
        return True
    
    
    def _compToPassport(self):
        fields = utils.extract_pdf(self.pdf_path)

        pdf_data = {
            "first_name": fields.get("account_holder_name").upper(),
            "last_name": fields.get("account_holder_surname").upper(),
            "passport_number": fields.get("passport_number"),
        }

        passport_text = utils.extract_png(self.passport_path)

        #compare info in the pdf to the information present in the passport text 
        
        mismatches = []

        for field in pdf_data.keys() :
            value = pdf_data[field]
            if not value :
                mismatches.append(f"{field} is missing in PDF")
            elif value.lower() not in passport_text:
                mismatches.append(f"mismatch for {field} : {value}")

        print("here is the passport text to compare: ", f"{passport_text}")
        return len(mismatches) == 0


    def _check_docx_pdf(self): 
        pdf_data = utils.extract_pdf(self.pdf_path)
        docx_data = utils.parse_docx(self.docx_path)
        data_match = True

        # fields to compare 
        field_ids = [("account_holder_name","first_middle_names"), 
                        ("account_holder_surname","last_name"), 
                        ("passport_number","id_passport_number"), 
                        ("country","country_of_domicile"), 
                        ("phone_number","telephone"), 
                        ("email","email")]

        mismatches = [0 if pdf_data.get(id1) == docx_data.get(id2) else 1 for id1, id2 in field_ids]

        if 1 in mismatches : 
            data_match = False

        addr = ["building_number", "postal_code", "city", "street_name"]
        for a in addr : 
            if pdf_data.get(a) not in docx_data.get("address"): 
                mismatches.append(1)
                data_match = False
            else:  
                mismatches.append(0)

        return data_match




if __name__ == "__main__" :
    cl = Classifier()
    direct = "client_data/"
    for f in sorted(os.listdir(direct)) :
        path = os.path.join(direct, f)
        
        num = int(path.split("_")[-1])
        expected = num <= 500
        predicted = cl.classify(path)
        
        if expected != predicted :
            print(path)