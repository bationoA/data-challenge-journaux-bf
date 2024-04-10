from src import Scraper
from src import Extractor


if __name__ == "__main__":
    print("Starting...")
    scraper = Scraper(n_threads=2)
    scraper.run()

    # extractor = Extractor()
    # extractor.run()

#
#
# import argparse
# import sys
#
# from src import Scraper
# from src import Extractor
#
# max_args_num = 2
# # Get the command-line arguments
# arguments = sys.argv
#
# tasks = ["scrap", "extract"]
#
# if __name__ == "__main__":
#     # Create an argument parser
#     parser = argparse.ArgumentParser(description="Description of your script")
#
#     # Add arguments with names and optional values
#     parser.add_argument("-t", type=str, help="Definit la tache a executer: s, e, or b pour scraping, extraction or "
#                                              "les deux, respectivement.")
#     parser.add_argument("-st", type=int, help="Nombre maximal de telechargement simultanes. Doit etre superieur a 0.")
#     parser.add_argument("-et", type=int, help="Nombre maximal de fichiers journal a traiter simultanement. Doit etre "
#                                               "superieur a 0.")
#
#     # If no arguments are provided, print help
#     # if len(sys.argv[1:]) == 0:
#     #     parser.print_help()
#     #     parser.exit()
#
#     # Parse the command-line arguments
#     args = parser.parse_args()
#     task = args.t
#     st = args.st
#     et = args.et
#
#     msg = ""
#
#     if task is None:
#         print("Task not provided: Use -t with s, e, or b for scrap, extract or both")
#         sys.exit(1)
#
#     if task == "s":
#         msg = "Task: Scrap"
#     elif task == "e":
#         msg = "Task: Extract"
#     else:
#         msg = "Task: Scrap and Extract"
#
#     if st is None:
#         st = 1
#     if st <= 0:
#         print("st cannot be negative or 0")
#         sys.exit(1)
#
#     if task in ["s", "b"] and st is not None:
#         msg += f" | Scrap Threads n: {st}"
#
#     if et is None:
#         et = 1
#     if et <= 0:
#         print("et cannot be negative or 0")
#         sys.exit(1)
#
#     if task in ["e", "b"] and et is not None:
#         msg += f" | Extract Threads n: {et}"
#
#     print("Starting...")
#     print(msg)
#     # print(f"is_torch_available(): {is_torch_available()}")
#
#     if task in ["s", "b"]:
#         scraper = Scraper(n_threads=st)
#         scraper.run()
#
#     if task in ["e", "b"]:
#         # print("extracting")
#         extractor = Extractor(n_threads=et)
#         extractor.run()
#         pass
