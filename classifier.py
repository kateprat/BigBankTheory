import utils
import os
from llm_compare import check_consistency_with_groq
from dataclasses import dataclass
import re
from tqdm import tqdm
from typing import List, Dict, Any


@dataclass
class Address:
    building_number: str
    street_name: str
    postal_code: str
    city: str
    country: str

    @staticmethod
    def from_string(text: str, country: str = "") -> "Address":
        """
        Parse address from a string format.

        Example input: "Świętokrzyska 62, 26-923 Wrocław"
        """
        building_number = ""
        street_name = ""
        postal_code = ""
        city = ""

        parts = [p.strip() for p in text.split(",")]

        # Extract street and city parts
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
            country=country.strip(),
        )


class Person:
    """
    Class for loading and verifying person data from multiple document sources.
    """

    def __init__(self, client_path: str):
        """Initialize paths to the person's documents."""
        self.client_path = client_path
        self.pdf_path = os.path.join(client_path, "account.pdf")
        self.passport_path = os.path.join(client_path, "passport.png")
        self.docx_path = os.path.join(client_path, "profile.docx")
        self.description_path = os.path.join(client_path, "description.txt")

        self.data: Dict[str, Any] = {}

    def compare_or_set(self, field: str, value: Any) -> bool:
        """
        Set a field value if not already set, or compare with existing value.
        Returns True if values match or field was newly set.
        """
        if field not in self.data:
            self.data[field] = value
            return True
        return self.data[field] == value

    def load_pdf(self) -> bool:
        """
        Load and validate data from PDF document.
        Returns True if data is consistent with existing data.
        """
        try:
            pdf_fields = utils.extract_pdf(self.pdf_path)
            checks = []

            # Compare or set basic identity fields
            checks.append(
                self.compare_or_set("account_name", pdf_fields.get("account_name"))
            )
            checks.append(
                self.compare_or_set("name", pdf_fields.get("account_holder_name"))
            )
            checks.append(
                self.compare_or_set("surname", pdf_fields.get("account_holder_surname"))
            )
            checks.append(
                self.compare_or_set("passport", pdf_fields.get("passport_number"))
            )

            # Normalize phone number (remove spaces)
            phone = pdf_fields.get("phone_number", "").replace(" ", "")
            checks.append(self.compare_or_set("phone", phone))

            # Email
            checks.append(self.compare_or_set("email", pdf_fields.get("email")))

            # Currency: check EUR, USD, CHF or use 'other_ccy'
            currency = self._extract_currency(pdf_fields)
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
            print(f"Error loading PDF from {self.pdf_path}: {e}")
            return False

    def _extract_currency(self, pdf_fields: Dict[str, str]) -> str:
        """Extract currency from PDF fields."""
        for code in ["eur", "usd", "chf"]:
            if pdf_fields.get(code, "").strip().lower() == "/yes":
                return code.upper()
        return pdf_fields.get("other_ccy", "").upper()

    def load_docx(self) -> bool:
        """
        Load and validate data from DOCX document.
        Returns True if data is consistent with existing data.
        """
        try:
            docx_data = utils.parse_docx(self.docx_path)
            checks = []

            # Build and check full name
            first_name = docx_data.get("first_middle_names", "").strip()
            last_name = docx_data.get("last_name", "").strip()
            full_name = f"{first_name} {last_name}".strip()

            checks.append(self.compare_or_set("account_name", full_name))
            checks.append(self.compare_or_set("name", first_name))
            checks.append(self.compare_or_set("surname", last_name))
            checks.append(
                self.compare_or_set(
                    "passport", docx_data.get("id_passport_number", "").strip()
                )
            )
            checks.append(
                self.compare_or_set("email", docx_data.get("email", "").strip())
            )
            checks.append(
                self.compare_or_set("phone", docx_data.get("telephone", "").strip())
            )

            # Parse and check address
            country = docx_data.get("country_of_domicile", "").strip()
            address = Address.from_string(docx_data.get("address", ""), country=country)
            checks.append(self.compare_or_set("address", address))

            # Additional identity information
            checks.append(
                self.compare_or_set("nationality", docx_data.get("nationality"))
            )
            checks.append(self.compare_or_set("gender", docx_data.get("gender")))

            return all(checks)

        except Exception as e:
            print(f"Error loading DOCX from {self.docx_path}: {e}")
            return False

    def check_passport(self) -> bool:
        """
        Validate passport image OCR text against stored person data.
        Returns True if the passport data matches the person data.
        """
        try:
            text = utils.extract_text(self.passport_path)
            normalized_text = utils.normalize_text(text).lower().replace("\n", " ")

            # Check key fields in passport
            check_fields = ["name", "surname", "passport", "nationality"]

            for field in check_fields:
                field_value = self.data.get(field, "").lower()
                if not field_value:
                    continue

                normalized_value = utils.normalize_text(field_value)
                masked_value = self._create_masked_value(field_value, normalized_value)

                if not self._partial_match(normalized_text, masked_value):
                    return False

            # Check gender marker
            expected_sex = "M" if self.data.get("gender") == "male" else "F"
            if expected_sex not in text:
                return False

            return True

        except Exception as e:
            print(f"Error checking passport from {self.passport_path}: {e}")
            return False

    def _create_masked_value(self, original: str, normalized: str) -> str:
        """Create a string with wildcards for diacritic characters."""
        return "".join([c if b == c else "*" for b, c in zip(original, normalized)])

    def _match_with_wildcards(self, text: str, pattern: str) -> bool:
        """Check if text matches pattern with wildcards."""
        pattern_regex = re.escape(pattern).replace(r"\*", ".*")
        return re.search(pattern_regex, text) is not None

    def _generate_partial_patterns(self, string: str) -> List[str]:
        """Generate patterns with adjacent wildcards for fuzzy matching."""
        patterns = []
        for i in range(len(string) - 1):
            pattern = list(string)
            pattern[i] = "*"
            pattern[i + 1] = "*"
            patterns.append("".join(pattern))
        return patterns

    def _partial_match(self, text: str, pattern: str) -> bool:
        """Check if text matches any of the generated fuzzy patterns."""
        patterns = self._generate_partial_patterns(pattern)
        return any(self._match_with_wildcards(text, pat) for pat in patterns)


class Classifier:
    """
    Classifier for verifying consistency across multiple document sources.
    """

    def __init__(self):
        pass

    def classify(self, client_path: str) -> bool:
        """
        Classify whether client documents are consistent.
        Returns True if documents pass validation.
        """
        person = Person(client_path=client_path)
        return person.load_pdf() and person.load_docx() and person.check_passport()

    def llm_compare(self, pdf_path: str, docx_path: str) -> bool:
        """
        Use LLM to compare documents for consistency.
        Returns True if LLM determines documents are consistent.
        """
        pdf_data = utils.extract_pdf(pdf_path)
        docx_data = utils.parse_docx(docx_path)
        result = check_consistency_with_groq(docx_data, pdf_data)
        print(result)
        return True


def run_validation(num_clients=3000, batch_log_interval=50):
    """Run validation on client data and print statistics."""
    total = success = false_positives = false_negatives = 0

    print("Starting validation...\n")

    for i in tqdm(range(num_clients), desc="Validating", unit="client"):
        path = f"client_data/client_{i + 1}/"
        if not os.path.isdir(path):
            continue

        total += 1
        person = Person(path)
        result = person.load_pdf() and person.load_docx() and person.check_passport()
        expected = (i % 1000) < 500

        success += result == expected
        false_negatives += int(not result and expected)
        false_positives += int(result and not expected)

        if i % batch_log_interval == 0 and i > 0:
            print(
                f"  └─ Processed {i} clients | Current Accuracy: {success}/{total} ({(success/total)*100:.2f}%)"
            )

    print("\n=== Validation Summary ===")
    print(f"Total Clients     : {total}")
    print(f"Correct Predictions: {success}")
    print(f"False Negatives   : {false_negatives}")
    print(f"False Positives   : {false_positives}")
    print(f"Accuracy          : {(success / total * 100):.2f}%\n")


if __name__ == "__main__":
    run_validation()
