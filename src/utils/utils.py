import os
import re
import json
import glob
import shutil
import hashlib
import pandas as pd
from tqdm import tqdm

# CONSTANTS
DATA_FOLDER = os.path.join("data")
TEMP_FOLDER = os.path.join("data", "temp")
CSV_FOLDER = os.path.join(DATA_FOLDER, "csv")
DOWNLOADED_FILES_FOLDER = os.path.join(DATA_FOLDER, "journaux")


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
    recepisse = "cepisse"
    recepisse = "\s?".join(recepisse)
    recepisse = "r?e?" + recepisse
    denomination = "denomination"
    denomination = "\s?".join(denomination)
    pattern = re.compile(rf"{keyword}.*?president.*?(?=\br?{recepisse}|{denomination}\b|$)", re.DOTALL)
    # pattern = re.compile(rf"\b{keyword}\b.*?(?=\b{keyword}\b|$)", re.DOTALL)
    # Find all matches of the pattern in the text
    sections = pattern.findall(txt)
    if len(sections):
        sections = [sc.strip() for sc in sections]

    return sections if not first else sections[0]


def remove_date_from_string(text):
    # Define a pattern to match the date at the end of the string
    pattern = r'\d{1,2}\s+(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+\d{4}$'

    # Use re.sub to replace the matched date with an empty string
    return re.sub(pattern, '', text)


def extract_declaration_numbers_and_dates(txt):
    txt = txt.lower().replace("é", "e")
    declaration = "declaration"
    declaration = "\s?".join(declaration)
    # declaration += "?\s?d?\s?\\?’?"
    declaration += "\s?d?\s?'?"
    declaration += "\s?".join("association")
    # Define the pattern to match the declaration numbers
    pattern = re.compile(r"\s?.*?" + declaration + "\s?(.*?du.*?\d{4})\.?")
    # Find all matches of the pattern in the text
    declaration_numbers = pattern.findall(txt)  # declaration numbers

    new_declaration_numbers = []
    tmp = declaration_numbers.copy()
    for dn_dt in tmp:
        new_match = dn_dt
        if len(dn_dt) >= 150:
            new_pattern = re.compile(r"(.*?\/+.*?\d{4})\.?")
            new_matches = new_pattern.findall(dn_dt)
            if len(new_matches):
                new_match = new_matches[0]
                _num = remove_date_from_string(new_match)
                _date = new_match.removeprefix(_num)
                new_match = _num + " du " + _date
            else:
                continue
        new_declaration_numbers.append(new_match)

        declaration_numbers.append(dn_dt)

    # Remove 'n°'
    declaration_numbers_dates = [dc.removeprefix("n°").removeprefix(" n").removeprefix('n"').split("du") for dc in
                                 new_declaration_numbers]
    # print(f"declaration_numbers_dates: {declaration_numbers_dates}")
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
    pattern = re.compile(rf"(?i)(?u)denomination:?\s*(.*?)(?:\s*en abrege|abrege|siege|\()", re.DOTALL)

    matches = re.findall(pattern, txt)
    name = matches[0].strip().upper() if len(matches) else ""
    if name != "":
        return name

    # --- Update the regex pattern and retry
    # Pattern to find the denomination
    denomination = "?".join("denomi")
    denomination += "?nation"
    pattern = re.compile(rf"(?i)(?u){denomination}:?\s*(.*?)(?:\s*en abrege|abrege|siege|\()", re.DOTALL)

    matches = re.findall(pattern, txt)
    return matches[0].strip().upper() if len(matches) else ""


def get_abbreviation_1(txt: str, denomination: str) -> str:
    """
    Pattern to find the abbreviation based on the denomination: denomination followed by abbreviation like '(A.S.K.)'
    """
    txt = txt.lower().replace("é", "e").replace("è", "e").replace('"', '').replace("'", "")

    # print(f"txt: {txt}")

    denomination = denomination.lower()

    pattern = re.compile(rf"{denomination}\s*\((.*?)\)\s")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt.lower())
    # print(f"matches: {matches}")
    abbreviation = matches[0].strip().upper() if len(matches) else ""
    if abbreviation == "":
        return ""
    abbreviation = abbreviation.removesuffix(".")

    # Check if abbreviation is a combination of words without .
    words = abbreviation.split(" ")
    if len(words) <= 1:
        return abbreviation  # If abbreviation does not contain any spaces

    words = [w for w in words if len(w) >= 2]  # Get words of more than 2 characters
    if len(words) == 0:
        return abbreviation  # Return abbreviation if all words are in fact single letters like (A B C)

    # If the extracted abbreviation is composed of words instead of single letters
    # Then the abbreviation is not a valid one
    return ""


def get_abbreviation_2(txt: str, denomination: str) -> str:
    txt = txt.replace("é", "e").lower().replace('"', '').replace("'", "")

    denomination = denomination.lower()

    # Pattern to find the abbreviation based on the denomination: denomination followed by abbreviation like '(A.S.K.)'
    pattern = re.compile(rf"{denomination}\s*en abrege\s*(\(?.*?\)?)\s")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt.lower())
    abbreviation = matches[0].strip().upper() if len(matches) else ""
    abbreviation = abbreviation.removesuffix(".")

    # Check if abbreviation is a combination of words without .
    words = abbreviation.split(" ")
    if len(words) <= 1:
        return abbreviation  # If abbreviation does not contain any spaces

    words = [w for w in words if len(w) >= 2]  # Get words of more than 2 characters
    if len(words) == 0:
        return abbreviation  # Return abbreviation if all words are in fact single letters like A B C

    return ""


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
    txt = txt.lower().replace("é", "e").replace("è", "e").replace('"', '').replace("'", "")
    txt = remove_special_characters(txt=txt)

    siege = "\s?".join("siege")
    end_with = ["objectif", "objet principal", "mission principal", "domaine dintervention", "a pour but", "objectif",
                "objet", "mission", "\s?".join("objectif"), "p?r?i?n?cipal"]
    end_with = "|".join(end_with)

    pattern = re.compile(rf"{siege}\s*?:?(.*?)(?:\s*{end_with}|,|\.)")

    # Find abbreviation in the text
    matches = re.findall(pattern, txt)
    siege = matches[0].strip().upper() if len(matches) else ""
    siege = siege.removesuffix(".")

    return siege


def get_objectifs(txt: str) -> str:
    txt = txt.lower().replace("é", "e").replace("è", "e").replace('"', '').replace("'", "")

    start_with = ["objectif principal", "objet principal", "mission principal", "domaine dintervention", "a pour but",
                  "objectifs?", "objet", "mission", "\s?".join("objectif"), "p?r?i?n?cipal"]

    end_with = ["la composition", "composition", "les noms", "prenoms", "noms", "prenoms", "nom", "prenom",
                "nom et prenom",
                "le bureau", "bureau", "domaine dintervention", "a pour but", "principaux dirigeants?", "dirigeant"]

    start_with = "|".join(start_with)
    end_with = "|".join(end_with)

    pattern = rf"\b(?:{start_with})(.*?)\b(?:{end_with})"
    pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)

    # Find abbreviation in the text
    matches = re.findall(pattern, txt)

    objectifs = matches[0].strip().capitalize() if len(matches) else ""

    return objectifs


def extract_association(section_text: str, dec_num_date: str) -> dict | None:
    """
    Extract information related to the association, excluding the members
    :param section_text:
    :param dec_num_date:
    :return:
    """
    association = dict()

    num, dt = dec_num_date
    section = extract_declaration_sections(keyword=num, txt=section_text, first=True)

    if section == "":
        return None

    # Association
    association['number'] = num
    association['date'] = dt
    association['denomination'] = get_association_name(txt=section)
    association['objective'] = get_objectifs(txt=section)
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

    details = extract_association(section_text=file_text, dec_num_date=dec_num_date)

    if details is None:
        print(f"dec_num_date: {dec_num_date}")
        return None

    association['details'] = details
    association['members'] = extract_members(section=section, roles=roles)

    return association


def add_to_dataframe(list_of_dicts: list, df: pd.DataFrame = None) -> pd.DataFrame:
    # Initialize an empty DataFrame
    if df is None:
        cols = list(list_of_dicts[0].keys())
        df = pd.DataFrame(columns=cols)

    # Iterate over each dictionary and append it to the DataFrame
    df = df.copy()
    df = pd.concat([df.copy(), pd.DataFrame(list_of_dicts)])

    return df.copy()


def generate_and_save_df(entity: str) -> pd.DataFrame | None:
    """
        Extract and save json temporary files of associations or members as csv
        :param entity: 'associations' OR 'members'
        :return:
        """
    if entity not in ['associations', 'members']:
        print(f"ERROR: 'entity' must be either 'associations' OR 'members'. {entity} was given.")
        return None
    list_tmp_names = os.listdir(os.path.join(TEMP_FOLDER, entity))

    list_tmp_paths = [os.path.join(TEMP_FOLDER, entity, name) for name in list_tmp_names]

    df = None
    for path in tqdm(list_tmp_paths):
        json_file = load_json(path)
        if len(json_file) != 0:
            df = add_to_dataframe(df=df, list_of_dicts=json_file)

    # Remove commas from all cells to avoid value overflow in other cells due to the presence if commas
    df = df.replace(',', '', regex=True)

    # Save as csv
    try:
        df.to_csv(os.path.join(CSV_FOLDER, f"{entity}.csv"), sep=";", index=False)
    except BaseException as e:
        print(f"{entity.title()} df SAVING ERROR: {e.__str__()}")
        return None

    return df


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
