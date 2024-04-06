from src.utils import DOWNLOADED_FILES_FOLDER, CSV_FOLDER


class Association:
    def __init__(self, id_: int, number: str, date: str, denomination: str, abbreviation: str, siege: str):
        self.id = id_
        self.number = number
        self.date = date
        self.denomination = denomination
        self.abbreviation = abbreviation
        self.siege = siege

    def __str__(self):
        return self.denomination


class Member:
    def __init__(self, assoc_id: int, full_name: str, position: str, phone_number: str, abbreviation: str, siege: str):
        self.assoc_id = assoc_id
        self.full_name = full_name
        self.position = position
        self.phone_number = phone_number

    def __str__(self):
        return self.full_name
