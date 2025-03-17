import math
import os
import time

from webpeditor.settings import STATIC_ROOT


def __delete_static_files(folder_path: str, with_extension: str) -> int:
    deleted_files_count = 0

    filenames = os.listdir(folder_path)

    if len(filenames) == 0:
        print(f"No files in folder '{folder_path}'")
        return 0

    for i, filename in enumerate(filenames):
        file_path = os.path.join(folder_path, filename)
        _, extension = os.path.splitext(filename)

        if not os.path.isfile(file_path) or with_extension not in extension:
            continue

        if math.ceil(time.time() - os.path.getctime(file_path)) > 86400:
            os.remove(file_path)
            deleted_files_count += i
            print(f"Deleted file: {filename}")

    if deleted_files_count == 0:
        print("No static files to delete")
        return 0

    return deleted_files_count


if __name__ == "__main__":
    deleted_files_total = 0
    deleted_files_total += __delete_static_files(os.path.join(STATIC_ROOT, "CACHE", "css"), "css")
    deleted_files_total += __delete_static_files(os.path.join(STATIC_ROOT, "CACHE", "js"), "js")

    print(f"Total deleted static files: {deleted_files_total}")
