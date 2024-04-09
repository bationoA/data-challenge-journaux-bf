import os
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from src.utils import DOWNLOADED_FILES_FOLDER, CSV_FOLDER, read_txt_file, extract_declaration_numbers_and_dates, \
    extract_declaration_sections, get_association_name, get_association_abbreviation, get_siege, get_objective


class Association:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.id = ""
        self.number = ""
        self.date = ""
        self.denomination = ""
        self.abbreviation = ""
        self.siege = ""
        self.objective = ""

    def __str__(self):
        return self.denomination

    def is_valid(self):
        if not self.id != "":
            return False
        # if not self.number != "":
        #     return False
        # if not self.date != "":
        #     return False
        if not self.denomination != "":
            return False
        # if not self.abbreviation != "":
        #     return False
        if not self.siege != "":
            return False
        if not self.objective != "":
            return False


class Member:
    def __init__(self, declaration_section: str):
        self.declaration_section = declaration_section
        self.assoc_id = ""
        self.full_name = ""
        self.position = ""

    def __str__(self):
        return self.full_name

    def is_valid(self):
        if not self.assoc_id != "":
            return False


class Extractor:
    def __init__(self, n_threads: int = 5):
        self.declaration_sections_n = 0
        self.files_names = os.listdir(DOWNLOADED_FILES_FOLDER)
        self.num_threads = n_threads
        self.associations = []

    def extract_details(self, file_name: str):
        # Read file
        file = read_txt_file(file_path=file_name)
        if file is None:
            return False

        # Extract association declaration number and date
        dec_num_dates_list = extract_declaration_numbers_and_dates(txt=file)

        # self.declaration_sections_n += dec_num_dates_list
        if "déclaration d'association" in file:
            self.declaration_sections_n += 1
            # print(f"found: {self.declaration_sections_n}")

        associations = []
        for num_dt in dec_num_dates_list:
            current_association = self.extract_association_details(file=file, dec_num_date=num_dt)
            associations.append(current_association)
            break

        self.associations += associations

    def extract_association_details(self, file: str, dec_num_date: str) -> dict:
        association = dict()

        num, dt = dec_num_date
        section = extract_declaration_sections(keyword=num, txt=file, first=True)

        # Association
        association['number'] = num
        association['date'] = dt
        association['denomination'] = get_association_name(txt=section)
        association['abbreviation'] = get_association_abbreviation(txt=section,
                                                                   denomination=association['denomination'])
        # association['siege'] = get_association_abbreviation(txt=section, denomination=association['denomination'])
        # association['siege'] = get_location(txt=section)
        # association['objective'] = get_objective(txt=section)

        # print(f"association: {association}")

        return association

    def extract_member_details(self, section: str):
        members = []

    def run(self):
        files_paths = [os.path.join(DOWNLOADED_FILES_FOLDER, file_name) for file_name in self.files_names]
        # print(f"files_paths: {files_paths}")
        print(f"files_paths: {len(files_paths)}")

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            executor.map(self.extract_details, files_paths)

        print(f"associations n: {len(self.associations)}")
        print(f"declaration_sections_n: {self.declaration_sections_n}")
        #
        # filepath = os.path.join("data", "associations.json")
        # print(f"self.associations: {self.associations}")
        # with open(filepath, 'w', encoding='utf-8') as f:
        #     json.dump(self.associations, f, ensure_ascii=False, indent=4)

        return True


""
