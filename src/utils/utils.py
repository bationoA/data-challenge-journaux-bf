import os
import re

# CONSTANTS
DOWNLOADED_FILES_FOLDER = os.path.join("data", "journaux")
CSV_FOLDER = os.path.join("data", "csv")


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


def extract_declaration_sections(txt, keyword):
    txt = txt.lower().replace("é", "e")
    # txt = remove_special_characters(txt=txt, keep=["(", ")", "."]).lower().replace("é", "e")
    # Compile a regular expression pattern to match sections based on the keyword
    pattern = re.compile(rf"\b{keyword}\b.*?(?=\b{keyword}\b|$)", re.DOTALL)
    # Find all matches of the pattern in the text
    sections = pattern.findall(txt)
    if len(sections):
        sections = [sc.strip() for sc in sections]
    return sections


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

    # If abbreviation not foound
    # Try pattern: denomination followed by abbreviation like 'A.S.K.'
    abbreviation = get_abbreviation_2(txt=txt, denomination=denomination)

    return abbreviation
