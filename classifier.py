import utils
import os
from llm_compare import check_consistency_with_groq
from dataclasses import dataclass
import re

@dataclass
class Address:
    building_number: str
    street_name: str
    postal_code: str
    city: str
    country: str

    @staticmethod
    def from_string(text: str, country: str = ""):
        # Example input: "Świętokrzyska 62, 26-923 Wrocław"
        building_number = ""
        postal_code = ""
        city = ""

        parts = [p.strip() for p in text.split(",")]

        if len(parts) == 2:
            street_part, city_part = parts
        elif len(parts) == 1:
            street_part = parts[0]
            city_part = ""
        else:
            street_part = parts[0]
            city_part = parts[-1]

        # Extract building number and street name
        match_street = re.search(r"^(.*?)(\d+[A-Za-z]?)$", street_part)
        if match_street:
            street_name = match_street.group(1).strip()
            building_number = match_street.group(2).strip()
        else:
            street_name = street_part
            building_number = ""

        # Match postal code (e.g., "741 24", "26-923", "12345", etc.)
        match_postal = re.search(r"(\d+[ -]?\d+)", city_part)
        if match_postal:
            postal_code = match_postal.group(1).strip()
            city = city_part.replace(postal_code, "").strip()
        else:
            city = city_part.strip()

        return Address(
            building_number=building_number,
            street_name=street_name,
            postal_code=postal_code,
            city=city,
            country=country.strip()
        )


class Person:
    def __init__(self, client_path):
        self.pdf_path = os.path.join(client_path, "account.pdf")
        self.passport_path = os.path.join(client_path, "passport.png")
        self.docx_path = os.path.join(client_path, "profile.docx")
        self.description_path = os.path.join(client_path, "description.txt")

        self.data = {}
        
    def compare_or_set(self, field, value) :
        if field not in self.data:
            self.data[field] = value
            return True
        else :
            # if self.data[field] != value :
            #     print(f"ERROR for field {field}, expected {self.data[field]}, got {value}")
            return self.data[field] == value
            

    def load_pdf(self):
        pdf_fields = utils.extract_pdf(self.pdf_path)

        try:
            checks = []

            # Compare or set basic identity fields
            checks.append(self.compare_or_set("account_name", pdf_fields.get("account_name")))
            checks.append(self.compare_or_set("name", pdf_fields.get("account_holder_name")))
            checks.append(self.compare_or_set("surname", pdf_fields.get("account_holder_surname")))
            checks.append(self.compare_or_set("passport", pdf_fields.get("passport_number")))

            # Normalize phone number (remove spaces)
            phone = pdf_fields.get("phone_number", "").replace(" ", "")
            checks.append(self.compare_or_set("phone", phone))

            # Email
            checks.append(self.compare_or_set("email", pdf_fields.get("email")))

            # Currency: check EUR, USD, CHF or use 'other_ccy'
            currency = ""
            for code in ["eur", "usd", "chf"]:
                if pdf_fields.get(code, "").strip().lower() == "/yes":
                    currency = code.upper()
                    break
            if not currency:
                currency = pdf_fields.get("other_ccy", "").upper()
            checks.append(self.compare_or_set("currency", currency))

            # Address
            address = Address(
                building_number=pdf_fields.get("building_number", ""),
                street_name=pdf_fields.get("street_name", ""),
                postal_code=pdf_fields.get("postal_code", ""),
                city=pdf_fields.get("city", ""),
                country=pdf_fields.get("country", ""),
            )
            checks.append(self.compare_or_set("address", address))

            return all(checks)

        except Exception as e:
            print("Error loading PDF:", e)
            return False

    def load_docx(self):
        docx_data = utils.parse_docx(self.docx_path)
        

        try:
            checks = []

            full_name = f"{docx_data.get('first_middle_names', '').strip()} {docx_data.get('last_name', '').strip()}"
            checks.append(self.compare_or_set("account_name", full_name))
            checks.append(self.compare_or_set("name", docx_data.get("first_middle_names", "").strip()))
            checks.append(self.compare_or_set("surname", docx_data.get("last_name", "").strip()))

            checks.append(self.compare_or_set("passport", docx_data.get("id_passport_number", "").strip()))

            checks.append(self.compare_or_set("email", docx_data.get("email", "").strip()))
            phone = docx_data.get("telephone", "").strip()
            checks.append(self.compare_or_set("phone", phone))

            country = docx_data.get("country_of_domicile", "").strip()
            address = Address.from_string(docx_data.get("address"), country=country)
            checks.append(self.compare_or_set("address", address))

            return all(checks)

        except Exception as e:
            print("Error loading DOCX:", e)
            return False


class Classifier:
    def __init__(self):
        pass

    def classify(self, client_path: str):
        person = Person(client_path=client_path)

        if not person.load_pdf():
            return False

        if not person.load_docx():
            return False

        return True


    def _llm_compare(self):
        pdf_data = utils.extract_pdf(self.pdf_path)
        docx_data = utils.parse_docx(self.docx_path)
        ans = check_consistency_with_groq(docx_data, pdf_data)
        print(ans)
        return True



if __name__ == "__main__":
    total = 0
    success = 0
    fp = 0
    fn = 0
    
    for i in range(3000) :
        path = "client_data/client_" + str(i + 1) + "/"
        if not os.path.isdir(path) : 
            continue
        
        total += 1
        pers = Person(path)
        
        result = pers.load_pdf() and pers.load_docx() 
        expected = (i % 1000) < 500
        
        success += result == expected
        
        if not result  and expected :
            fn += 1
        if result and not expected :
            fp += 1
            
        if result != expected :
            print(path)
        
        
    print(total, success, fn, fp)
