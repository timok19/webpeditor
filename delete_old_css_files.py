import os
import time
from pprint import pprint

from webpeditor.settings import STATIC_ROOT


if __name__ == "__main__":
    path_to_css = os.path.join(STATIC_ROOT, "CACHE", "css")
    files = os.listdir(path_to_css)

    deleted_files_count = 0

    for i, file in enumerate(files, start=1):
        file_path = os.path.join(path_to_css, file)

        file_name, file_extension = os.path.splitext(file)

        if not os.path.isfile(file_path) and ".css" not in file_extension:
            pprint("There is no css file to delete")
            break

        creation_time = os.path.getctime(file_path)

        if int(time.time() - creation_time) > 86400:
            os.remove(file_path)
            deleted_files_count += i
            pprint(f"Deleted file: {file_name}{file_extension}")

    pprint(f"Total deleted CSS files: {deleted_files_count}")
