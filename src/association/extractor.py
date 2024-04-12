import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from src.utils import DOWNLOADED_FILES_FOLDER, read_txt_file, extract_declaration_numbers_and_dates, DATA_FOLDER, \
    load_json, extract_association_details, clean_text, generate_declaration_id, save_to_json, TEMP_FOLDER, \
    generate_and_save_df


class Extractor:
    def __init__(self, n_threads: int = 5):
        self.declaration_sections_n = 0
        self.files_names = os.listdir(DOWNLOADED_FILES_FOLDER)
        self.num_threads = n_threads
        self.associations_details = []
        self.associations_members = []
        self.roles = load_json(filepath=os.path.join(DATA_FOLDER, "roles.json"))
        self.ignore_files = load_json(filepath=os.path.join(DATA_FOLDER, "ignore_files.json"))
        self.base_url = "https://www.loc.gov/resource"

    def extract_details(self, file_name: str):
        # Read file
        journal_id = file_name.split("file_")[1].removesuffix(".txt")
        file = read_txt_file(file_path=file_name)
        if file is None:
            return False

        # Clean text file content
        file_content = clean_text(txt=file)

        # Extract association declaration number and date
        dec_num_dates_list = extract_declaration_numbers_and_dates(txt=file_content)

        # print(f"dec_num_dates_list: {dec_num_dates_list}")

        # Extract associations
        associations_details = []
        associations_members = []
        for dec_num_date in tqdm(dec_num_dates_list):
            new_association = extract_association_details(file_text=file_content, dec_num_date=dec_num_date,
                                                          roles=self.roles)
            if new_association is None:
                print(f"No association found for dec_num_date '{dec_num_date}' \n file '{file_name}'")
                continue
            assoc_id = generate_declaration_id(val=dec_num_date[0])
            new_details = new_association["details"].copy()
            new_details["id"] = assoc_id
            new_details["journal_link"] = self.base_url+"/"+journal_id

            new_members = [
                {
                    "association_id": assoc_id,
                    "role": list(member.keys())[0],
                    "name": list(member.values())[0],
                } for member in new_association["members"]
            ]

            associations_details.append(new_details)
            associations_members += new_members

        # Save items as json
        try:
            prefix = file_name.split("file_")[1].removesuffix(".txt")
            tmp_assoc_path = os.path.join(TEMP_FOLDER, "associations", f"{prefix}.json")
            tmp_members_path = os.path.join(TEMP_FOLDER, "members", f"{prefix}.json")

            save_to_json(obj=associations_details, filepath=tmp_assoc_path)
            save_to_json(obj=associations_members, filepath=tmp_members_path)
        except BaseException as e:
            print(e.__str__())
            return False

        return True

    def apply_ignore_files(self):
        """
        Filter out files names by excluding the ones that we decide to ignore
        :return:
        """
        tmp = self.files_names.copy()
        self.files_names = [_ for _ in tmp if _ not in self.ignore_files]

    def run(self):
        # Applying 'ignore files'
        self.apply_ignore_files()
        print(f"Nombre de journaux a traiter: {len(self.files_names)}...")

        files_paths = [os.path.join(DOWNLOADED_FILES_FOLDER, file_name) for file_name in self.files_names]

        # files_paths = files_paths[0:5]  # TODO: Remove

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            executor.map(self.extract_details, files_paths)

        # Combine and save associations and their members as csv files
        df_associations = generate_and_save_df(entity="associations")  # For associations
        df_members = generate_and_save_df(entity="members")  # For members

        print(f"Task Complete\n")
        print(f"------------------RESUME-----------------\n")
        print(f"> Nombre total d'associations trouves: {df_associations.shape[0]}\n")
        print(f"> Nombre total membres trouves: {df_members.shape[0]}\n")
        print(f"------------------END-----------------\n")


        return True
