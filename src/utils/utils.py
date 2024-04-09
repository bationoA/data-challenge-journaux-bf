import os
import re
import json

# CONSTANTS
DOWNLOADED_FILES_FOLDER = os.path.join("data", "journaux")
CSV_FOLDER = os.path.join("data", "csv")


def clean_text(txt):
    # Replace special characters with spaces
    cleaned_text = re.sub(r'[•*■]', ' ', txt)

    # Remove unnecessary newlines and extra spaces
    cleaned_text = re.sub(r'\n+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Correct spacing around punctuation marks
    cleaned_text = re.sub(r'\s([.,:;!?])', r'\1', cleaned_text)
    cleaned_text = re.sub(r'([.,:;!?])\s', r'\1 ', cleaned_text)

    return cleaned_text.strip()


def remove_special_characters(txt, keep: list = None):
    # Define the pattern to match special characters
    # pattern = r'[^\w\s]'
    special_chars = "!@#$%^&*()-_=+[]{};:'\",.<>/?\|`~"

    if keep is not None:
        for sch in keep:
            special_chars = special_chars.replace(f"{sch}", "")

    for sp in list(special_chars):
        txt = txt.replace(sp, "")
    return txt


def extract_declaration_sections(txt, keyword, first=True):
    txt = txt.lower().replace("é", "e")
    # Compile a regular expression pattern to match sections based on the keyword
    recepisse = "cepisse"
    recepisse = "\s?".join(recepisse)
    recepisse = "r?e?" + recepisse
    denomination = "denomination"
    denomination = "\s?".join(denomination)
    pattern = re.compile(rf"\b{keyword}\b.*?president.*?(?=\br?{recepisse}|{denomination}\b|$)", re.DOTALL)
    # pattern = re.compile(rf"\b{keyword}\b.*?(?=\b{keyword}\b|$)", re.DOTALL)
    # Find all matches of the pattern in the text
    sections = pattern.findall(txt)
    if len(sections):
        sections = [sc.strip() for sc in sections]

    return sections if not first else sections[0]


def extract_declaration_numbers_and_dates(txt):
    txt = txt.lower().replace("é", "e")
    declaration = "declaration"
    declaration = "\s?".join(declaration)
    # declaration += "?\s?d?\s?\\?’?"
    declaration += "\s?d?\s?'?"
    declaration += "\s?".join("association")
    # Define the pattern to match the declaration numbers
    pattern = re.compile(r"\s?.*?" + declaration + "\s?(.*?du.*?\d{4})")
    # Find all matches of the pattern in the text
    declaration_numbers = pattern.findall(txt)
    # Remove 'n°'
    declaration_numbers_dates = [dc.removeprefix("n°").removeprefix(" n").removeprefix('n"').split("du") for dc in
                                 declaration_numbers]
    results = []
    for dn_dt in declaration_numbers_dates:
        try:
            new_dn_dt = dn_dt[0].strip(), dn_dt[1].strip() if len(dn_dt) == 2 else dn_dt[0].strip()
            results.append(new_dn_dt)
        except:
            pass

    return results


# def extract_declaration_numbers_and_dates_old(txt):
#     txt = txt.lower()
#     declaration = "declaration"
#     declaration = "\s?".join(declaration)
#     declaration += "?\s?d?\s?’?"
#     declaration += "\s?".join("association")
#     # Define the pattern to match the declaration numbers
#     # pattern = re.compile(r"\s?.*?c\s?e\s?p\s?(.*?)\d{4}")
#     pattern = re.compile(r"\s?.*?" + declaration + "\s?(.*?\d{4})")
#     # Find all matches of the pattern in the text
#     declaration_numbers = pattern.findall(txt)
#     # Remove 'n°'
#     declaration_numbers_dates = [dc.removeprefix("n°").split("du") for dc in declaration_numbers]
#     results = []
#     for dn_dt in declaration_numbers_dates:
#         try:
#             new_dn_dt = dn_dt[0].strip(), dn_dt[1].strip() if len(dn_dt) == 2 else dn_dt[0].strip()
#             results.append(new_dn_dt)
#         except:
#             pass
#
#     return results


def get_association_name(txt: str) -> str:
    txt = txt.replace("é", "e").lower()

    txt = remove_special_characters(txt=txt, keep=["(", ")"])

    # Pattern to find the denomination
    pattern = re.compile(r"(?i)(?u)denomination:?\s*(.*?)(?:\s*en abrege|abrege|siege|\()", re.DOTALL)

    matches = re.findall(pattern, txt)
    return matches[0].strip().upper() if len(matches) else ""


def get_abbreviation_1(txt: str, denomination: str) -> str:
    """
    Pattern to find the abbreviation based on the denomination: denomination followed by abbreviation like '(A.S.K.)'
    """
    txt = txt.lower().replace("é", "e").replace('"', '').replace("'", "")

    denomination = denomination.lower()

    pattern = re.compile(rf"{denomination}\s*\((.*?)\)\s")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt.lower())
    abbreviation = matches[0].strip().upper() if len(matches) else ""
    abbreviation = abbreviation.removesuffix(".")

    return abbreviation


def get_abbreviation_2(txt: str, denomination: str) -> str:
    txt = txt.replace("é", "e").lower().replace('"', '').replace("'", "")

    denomination = denomination.lower()

    # Pattern to find the abbreviation based on the denomination: denomination followed by abbreviation like '(A.S.K.)'
    pattern = re.compile(rf"{denomination}\s*en abrege\s*(\(?.*?\)?)\s")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt.lower())
    abbreviation = matches[0].strip().upper() if len(matches) else ""
    abbreviation = abbreviation.removesuffix(".")

    return abbreviation


def get_association_abbreviation(txt: str, denomination: str = None) -> str:
    # txt = txt.lower()
    if denomination is None:
        denomination = get_association_name(txt)

    txt = remove_special_characters(txt=txt, keep=["(", ")"])

    denomination = re.escape(denomination)

    # Try pattern: denomination followed by abbreviation like '(A.S.K.)'
    abbreviation = get_abbreviation_1(txt=txt, denomination=denomination)

    # Return abbreviation if found
    if abbreviation != "":
        return abbreviation

    # If abbreviation not found
    # Try pattern: denomination followed by abbreviation like 'A.S.K.'
    abbreviation = get_abbreviation_2(txt=txt, denomination=denomination)

    return abbreviation


def get_siege(txt: str) -> str:
    return ""


def get_objective(txt: str) -> str:
    return ""


def read_txt_file(file_path: str) -> str | None:
    try:
        with open(file_path, "r") as f:
            return f.read()
    except BaseException as e:
        print(f"Error: {e.__str__()}")
        return None


def load_json(filepath: str) -> json:
    with open(filepath, 'r') as f:
        file = json.load(f)

    return file
