import os
import logging
from time import time

from tqdm import tqdm
from selenium import webdriver  # for simulating user action such as a click on a button
from src.utils import DOWNLOADED_FILES_FOLDER, delete_chromium_temp_files
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options  # Options while setting up the webdriver with chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC


class Scraper:
    def __init__(self, n_threads: int = 2):
        self.base_url = "https://www.loc.gov/search/?fa=partof:burkina+faso+legal+gazettes"
        self.starting_page_number = 5
        self.all_publication_urls = []  # Contains the list of all publications urls
        self.document = {}  # 'id', 'pages': ['page': 1, 'content': "the content"]
        self.time_wait_till_visible = 10  # Time in seconds to wait till a given element is loaded in the DOM

        # Configure logging
        logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

        self.num_threads = n_threads  # Number of threads

        self.last_chromium_clean_time = time()
        self.chromium_cleaning_interval = 10  # In seconds

    def run(self):
        # Collect all publication urls
        self.get_all_publication_urls()

        # Filter urls by removing urls those document have already been downloaded
        self.filter_urls()

        # Construct all documents
        self.construct_and_save_all_documents()

    def generate_publications_list_page_url(self, page: int) -> str:
        """
        Generate url of the publication list web page
        :param page:
        :return:
        """
        return self.base_url + f"&sp={page}"

    def get_page(self, url: str, wait_till_visible: tuple | None = None,
                 wait_time: int | None = None) -> WebDriver | None:
        """

        :param url:
        :param wait_till_visible:
        :param wait_time:
        :return:
        """
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument(
            "--headless")  # Run Chrome in headless mode: Without opening the Chrome browser in a visible window

        # Set up web driver with Chrome options
        # driver = webdriver.Chrome()  # show browser
        driver = webdriver.Chrome(options=chrome_options)  # Hide browser


        try:
            # Navigate to the website
            driver.get(url)

            if wait_time is None:
                wait_time = self.time_wait_till_visible

            if wait_time is not None:
                WebDriverWait(driver, wait_time).until(EC.visibility_of_element_located(wait_till_visible))
        except BaseException as e:
            # Log the error message with level ERROR
            print(url)
            logging.error(e.__str__())
            return None

        return driver

    def get_one_page_publication_urls(self, driver: WebDriver) -> (list, bool):
        urls = []
        try:
            div_content = driver.find_element(By.CLASS_NAME, "content")
            div_main = div_content.find_element(By.ID, "main")
            item_pages = div_main.find_elements(By.XPATH, "//li[contains(@class, 'item')]")

            for li in item_pages:
                # (By.XPATH, "//a[substring(@href, string-length(@href) - string-length('text') +1) = 'text']")
                a_list = li.find_elements(By.TAG_NAME, "a")
                for a in a_list:
                    if a.get_attribute("href").endswith("st=text"):
                        urls.append(a.get_attribute("href"))
        except BaseException as e:
            # Log the error message with level ERROR
            logging.error(e.__str__())
            return []

        next_exists = len(driver.find_elements(By.XPATH, "//a[@class='next']")) != 0

        return urls, next_exists

    def get_all_publication_urls(self):
        next_page_exist = True
        driver_main: WebDriver | None = None
        current_page_number = self.starting_page_number
        print("\r", "Collecting urls... ", end="")
        while next_page_exist:
            page_url = self.generate_publications_list_page_url(page=current_page_number)

            driver_main = self.get_page(url=page_url, wait_till_visible=(By.CLASS_NAME, "content"))

            if driver_main is None:
                # print("Failed.")
                break

            # print("Success!")
            new_urls_list, next_page_exist = self.get_one_page_publication_urls(driver=driver_main)

            self.all_publication_urls += new_urls_list

            print(end=f"\r Loaded page(s): {current_page_number}, publications n: {len(self.all_publication_urls)}")

            if next_page_exist:
                current_page_number += 1

            self.clean_chromium_temp_files()

        if WebDriver is not None:
            driver_main.quit()  # Close driver

        return

    # -------------- Download text
    def filter_urls(self):

        print(f"  Number of retrieved urls:{len(self.all_publication_urls)}")

        files_list = os.listdir(DOWNLOADED_FILES_FOLDER)
        print(f"  Number of downloaded files:{len(files_list)}")

        downloaded_files_ids = [name.removeprefix("file_").removesuffix(".txt") for name in files_list]

        filtered_urls = [url for url in self.all_publication_urls
                         if not any([name in url for name in downloaded_files_ids])]

        self.all_publication_urls = filtered_urls.copy()

        print(f"  Number of documents to download:{len(self.all_publication_urls)}")

    def generate_publication_page_url(self, url: str, page: int) -> str:
        """
        Generate url of a specific publication web page
        :param url: url ending with '/?st=text'
        :param page: Document current page number
        :return: return an url for the current page number of the current publication
        """
        return url.replace("?", f"?sp={page}&").replace("&&", "&")

    def construct_document(self, url: str) -> bool:
        """
        Get of all pages of a publication and put the together to make a full text
        :param url: publication text url
        :return:
        """
        print(f"   Starting assessing url: {url}...")
        text = ""
        try:
            # Get total number of pages
            driver = self.get_page(url=url, wait_till_visible=(By.ID, "fulltext-box"), wait_time=20)
            select_page = driver.find_element(By.XPATH, "//select[@id='page']")
            option_text = select_page.find_element(By.TAG_NAME, "option").text
            total_pages = int(option_text.split("of")[1].strip())
            driver.quit()  # Close driver

            print(f"   Pages to merge: {total_pages} - ({url})")
            for i in tqdm(range(1, total_pages + 1)):
                current_url = self.generate_publication_page_url(url=url, page=i)
                # driver = self.get_page(url=current_url, wait_till_visible=(By.ID, "fulltext-box"), wait_time=20)
                #
                # if driver is None:
                #     return False

                try:
                    driver = self.get_page(url=current_url, wait_till_visible=(By.ID, "fulltext-box"), wait_time=20)
                    div_fulltext_box = driver.find_element(By.ID, "fulltext-box")
                    text += f""" 
                    PAGE {i}
                    {div_fulltext_box.text}
                    """
                except BaseException as e:
                    # Log the error message with level ERROR
                    logging.error(e.__str__())
                    print("\n Continuing...")

                self.clean_chromium_temp_files()

            # Save text as a txt file
            file_name = "file_" + url.split("/")[-2]

            with open(os.path.join(DOWNLOADED_FILES_FOLDER, file_name + ".txt"), 'w') as f:
                f.write(text)
        except BaseException as e:
            print(f"error: {e.__str__()}")

        return True

    def construct_and_save_all_documents(self):
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            executor.map(self.construct_document, self.all_publication_urls)

        return True

    def clean_chromium_temp_files(self):
        if time() - self.last_chromium_clean_time >= self.chromium_cleaning_interval:
            delete_chromium_temp_files()
            self.last_chromium_clean_time - time()
