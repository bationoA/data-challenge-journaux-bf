import os
import re
import json
import glob
import shutil
import hashlib

# CONSTANTS
DATA_FOLDER = os.path.join("data")
TEMP_FOLDER = os.path.join("data", "temp")
DOWNLOADED_FILES_FOLDER = os.path.join(DATA_FOLDER, "journaux")
CSV_FOLDER = os.path.join(DATA_FOLDER, "csv")

import re


def remove_journal_header(text):
    # Define the pattern to match
    pattern = r"PAGE \d+ \d+ JOURNAL OFFICIEL DU BURKINA FASO N°\d+ \d+ \w+ \d+"

    cleaned_text = re.sub(pattern, "", text)

    return cleaned_text


def clean_text(txt):
    # Replace special characters with spaces
    cleaned_text = re.sub(r'[•*■]', ' ', txt)

    # Remove unnecessary newlines and extra spaces
    cleaned_text = re.sub(r'\n+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Correct spacing around punctuation marks
    cleaned_text = re.sub(r'\s([.,:;!?])', r'\1', cleaned_text)
    cleaned_text = re.sub(r'([.,:;!?])\s', r'\1 ', cleaned_text)

    cleaned_text = remove_journal_header(cleaned_text)

    return cleaned_text.strip()


def fix_formatting(txt):
    # text_ = process_text(text_)
    txt = clean_text(txt)

    # Split the text_ into lines
    lines = txt.split("\n")
    # Initialize a list to hold the fixed lines
    fixed_lines = []
    # Iterate over each line
    for line in lines:
        # If the line is empty or contains only whitespace, skip it
        if not line.strip():
            continue
        # Remove leading and trailing whitespace from the line
        line = line.strip()
        # Append the fixed line to the list
        fixed_lines.append(line)
    # Join the fixed lines into a single string with newline characters
    fixed_text = "\n".join(fixed_lines)
    fixed_text = fixed_text.replace("n°", "numero").replace("N°", "numero")
    return fixed_text


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
    # pattern = re.compile(rf"\b{keyword}\b.*?president.*?(?=\br?{recepisse}|{denomination}\b|$)", re.DOTALL)
    pattern = re.compile(rf"{keyword}.*?president.*?(?=\br?{recepisse}|{denomination}\b|$)", re.DOTALL)
    # pattern = re.compile(rf"\b{keyword}\b.*?(?=\b{keyword}\b|$)", re.DOTALL)
    # Find all matches of the pattern in the text
    sections = pattern.findall(txt)
    if len(sections):
        sections = [sc.strip() for sc in sections]
    else:
        return ""

    return sections if not first else sections[0]


def extract_declaration_numbers_and_dates(txt):
    txt = txt.lower().replace("é", "e")
    declaration = "declaration"
    declaration = "\s?".join(declaration)
    # declaration += "?\s?d?\s?\\?’?"
    declaration += "\s?d?\s?'?"
    declaration += "\s?".join("association")
    # Define the pattern to match the declaration numbers
    pattern = re.compile(r"\s?.*?" + declaration + "\s?(.*?du?.*?\d{4}\.?)")
    # Find all matches of the pattern in the text
    declaration_numbers = pattern.findall(txt)
    # Remove 'n°'
    declaration_numbers_dates = []
    for dc in declaration_numbers:
        dc = dc.removeprefix("n°").removeprefix(" n").removeprefix('n"').removesuffix(".")
        if "du" in dc:
            declaration_numbers_dates.append([_.strip() for _ in dc.split("du")])
        else:
            split_dc = dc.split(" ")
            dc_num = " ".join(split_dc[0:-3])
            dc_date = " ".join(split_dc[-3:])
            declaration_numbers_dates.append((dc_num, dc_date))
    # declaration_numbers_dates = [dc.removeprefix("n°").removeprefix(" n").removeprefix('n"').split("du") for dc in
    #                              declaration_numbers]
    results = []
    for dn_dt in declaration_numbers_dates:
        try:
            new_dn_dt = dn_dt[0].strip(), dn_dt[1].strip() if len(dn_dt) == 2 else dn_dt[0].strip()
            results.append(new_dn_dt)
        except:
            pass

    return results


def get_association_name(txt: str) -> str:
    txt = txt.replace("é", "e").replace("è", "e").lower()

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


def get_siege(txt: str) -> str:
    txt = txt.lower().replace("é", "e").replace("è", "e").replace('"', '').replace("'", "")
    txt = remove_special_characters(txt=txt)

    # print(txt)

    siege = "\s?".join("siege")
    objectif = "\s?".join("objectif")

    pattern = re.compile(rf"{siege}\s*?:?(.*?)(?:\s*{objectif}|,|\.)")

    # print(f"\n{pattern}")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt)
    siege = matches[0].strip().upper() if len(matches) else ""
    siege = siege.removesuffix(".")

    return siege


def get_objectifs(txt: str) -> str:
    txt = txt.lower().replace("é", "e").replace("è", "e").replace('"', '').replace("'", "")
    # txt = remove_special_characters(txt=txt)

    # print(txt)

    # denomination = denomination.lower()

    objectif = "\s?".join("objectif")

    stop_at = ["la composition", "les noms", "prenoms", "noms", "prenoms", "nom", "prenom", "nom et prenom", "noms",
               "le bureau", "bureau", "domaine d'intervention", "a pour but"]

    stop_at = "|".join(stop_at)

    pattern = re.compile(
        rf"{objectif}s?(.*?)(?:\s*{stop_at})")

    # print(f"\n{pattern}")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt)
    objectifs = matches[0].strip().capitalize() if len(matches) else ""

    return objectifs


def extract_association(file: str, dec_num_date: str) -> dict | None:
    """
    Extract information related to the association, excluding the members
    :param file:
    :param dec_num_date:
    :return:
    """
    association = dict()

    num, dt = dec_num_date
    section = extract_declaration_sections(keyword=num, txt=file, first=True)

    if section == "":
        return None

    # Association
    association['number'] = num
    association['date'] = dt
    association['denomination'] = get_association_name(txt=section)
    association['objective'] = get_objectifs(txt=section)
    if association['denomination'] == "" or association['objective'] == "":
        return None
    association['abbreviation'] = get_association_abbreviation(txt=section, denomination=association['denomination'])
    association['siege'] = get_siege(txt=section)

    return association


def extract_members(section: str, roles: list) -> list[dict]:
    """
    Extract the members of the association together with their respective role.
    :param section:
    :param roles:
    :return:
    """
    members = dict()

    section += "."  # Add a full stop at the end of the section. It will be important when extracting the last member
    # in the section

    section = section.replace("é", "e").replace("è", "e").replace("à", "a").lower()
    # print(section)
    # print("\n")

    copy_positions = roles.copy()
    roles = [pos.replace("é", "e").replace("è", "e").replace("à", "a").lower() for pos in copy_positions]

    for position in roles:
        curr_position = position.replace("é", "e").replace("è", "e").replace("à", "a").lower()

        other_positions = [pos for pos in roles if pos != curr_position]

        other_positions_base = [pos.split(" ")[0] for pos in other_positions]
        other_positions_base = set(other_positions_base)  # Remove duplicates

        stop_at = "|".join(other_positions_base)
        # stop_at = "vice-president"

        # pattern = re.compile(rf"{curr_position}\s*?:?(.*?)(?:\s*,|\.|{stop_at})")
        pattern = re.compile(rf"{curr_position}\s*?:?(.*?)(?:\s*{stop_at})")
        # print(f"\n{pattern}")

        # Find abbreviation in the text
        matches = re.findall(pattern, section)
        person = matches[0].strip().upper() if len(matches) else ""
        person = person.removesuffix(".")

        members[curr_position] = person

    return [{key.upper(): members[key]} for key in members.keys() if members[key] != ""]


def extract_association_details(file_text: str, dec_num_date: str, roles: list) -> dict | None:
    """
    Extract information related to the association, excluding the members
    :param file_text:
    :param dec_num_date:
    :param roles:
    :return:
    """
    association = dict()

    num, dt = dec_num_date
    section = extract_declaration_sections(keyword=num, txt=file_text, first=True)
    association["declaration number"] = dec_num_date

    details = extract_association(file=file_text, dec_num_date=dec_num_date)

    if details is None:
        return None

    association['details'] = extract_association(file=file_text, dec_num_date=dec_num_date)
    association['members'] = extract_members(section=section, roles=roles)

    return association


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


def save_to_json(obj: list | dict, filepath: str) -> bool:
    save_status = True
    # Check object is in a valid json format
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

    return True


def generate_md5(input_string):
    # Encode the input string to bytes and calculate MD5 hash
    md5_hash = hashlib.md5(input_string.encode()).hexdigest()
    return md5_hash


def generate_declaration_id(val: str) -> str:
    return generate_md5(input_string=val)


def delete_chromium_temp_files():
    """
    Free memory by removing temp files created by Chromium and Selenium
    :return:
    """
    # Get a list of directories matching the pattern
    directory_pattern = "/tmp/.org.chromium.Chromium*"
    directories_to_delete = glob.glob(directory_pattern)

    # Delete each directory
    for directory_path in directories_to_delete:
        try:
            shutil.rmtree(directory_path)
        except OSError as e:
            print(f"Error deleting directory '{directory_path}': {e}")
