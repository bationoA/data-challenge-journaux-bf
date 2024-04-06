from transformers import is_torch_available

from src import Scraper

scraper = Scraper()
if __name__ == "__main__":
    print("Starting...")
    # print(f"is_torch_available(): {is_torch_available()}")
    scraper.run()
