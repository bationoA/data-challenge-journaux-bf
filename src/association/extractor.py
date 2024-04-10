import os
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from src.utils import DOWNLOADED_FILES_FOLDER, CSV_FOLDER, read_txt_file, extract_declaration_numbers_and_dates, \
    extract_declaration_sections, get_association_name, get_association_abbreviation, DATA_FOLDER, load_json, \
    extract_association, extract_association_details, clean_text, generate_declaration_id, save_to_json, TEMP_FOLDER


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
        self.associations_details = []
        self.associations_members = []
        self.roles = load_json(filepath=os.path.join(DATA_FOLDER, "roles.json"))

    def extract_details(self, file_name: str):
        # Read file
        print(f"file_name: {file_name}")
        file = read_txt_file(file_path=file_name)
        if file is None:
            return False

        # Clean text file content
        file_content = clean_text(txt=file)
        print("Cleaned.")

        # Extract association declaration number and date
        dec_num_dates_list = extract_declaration_numbers_and_dates(txt=file_content)
        print("Declarations numbers extracted.")

        # print(f"dec_num_dates_list: {dec_num_dates_list}")

        # Extract associations
        associations_details = []
        associations_members = []
        print("Starting loop for")
        for dec_num_date in tqdm(dec_num_dates_list):
            new_association = extract_association_details(file_text=file_content, dec_num_date=dec_num_date,
                                                          roles=self.roles)
            if new_association is None:
                print(f"No association found for dec_num_date '{dec_num_date}' \n file '{file_name}'")
                print(file_content)
                continue
            assoc_id = generate_declaration_id(val=dec_num_date[0])
            new_details = {
                "id": assoc_id,
                "declaration number": dec_num_date,
                "details": new_association["details"]
            }
            new_members = [
                {
                    "asso_id": file_name,#assoc_id,
                    "name": list(member.values())[0],
                    "role": list(member.keys())[0],
                } for member in new_association["members"]
            ]

            associations_details.append(new_details)
            associations_members += new_members
        print("Ending loop for")

        # Save items as json
        print(f"Saving file: {file_name}")
        try:
            prefix = file_name.split("file_")[1].removesuffix(".txt")
            tmp_assoc_path = os.path.join(TEMP_FOLDER, "associations", f"{prefix}.json")
            tmp_members_path = os.path.join(TEMP_FOLDER, "members", f"{prefix}.json")

            save_to_json(obj=associations_details, filepath=tmp_assoc_path)
            save_to_json(obj=associations_members, filepath=tmp_members_path)
        except BaseException as e:
            print(e.__str__())
            return False
        print(f"Done Saving file: {file_name}")

        return True

    def build_csvs(self):
        # For Association
        pass

    def run(self):
        files_paths = [os.path.join(DOWNLOADED_FILES_FOLDER, file_name) for file_name in self.files_names]
        # print(f"files_paths: {files_paths}")
        print(f"files_paths: {len(files_paths)}")

        files_paths = files_paths[0:10]
        # for file_path in files_paths:
        #     print(f"file_path: {file_path}")
        #     self.extract_details(file_path)

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            executor.map(self.extract_details, files_paths)

        return True


""
