import math
import os
import time
from datetime import UTC, datetime
from typing import Final

from webpeditor.settings import STATIC_ROOT


def delete_static_files(folder_path: str, with_extension: str) -> int:
    deleted_files_count = 0
    one_day_in_seconds: Final[int] = 86400

    try:
        filenames = os.listdir(folder_path)
    except FileNotFoundError:
        print(f"Folder not found: '{folder_path}'")
        return 0
    except PermissionError:
        print(f"Permission denied when accessing folder: '{folder_path}'")
        return 0

    if len(filenames) == 0:
        print(f"No files in folder '{folder_path}'")
        return 0

    for filename in filenames:
        file_path = os.path.join(folder_path, filename)
        _, extension = os.path.splitext(filename)

        if not os.path.isfile(file_path) or with_extension not in extension:
            continue

        file_age_in_seconds = math.ceil(time.time() - os.path.getctime(file_path))
        if file_age_in_seconds > one_day_in_seconds:
            try:
                os.remove(file_path)
                deleted_files_count += 1
                print(f"Deleted file: {filename}")
            except (PermissionError, OSError) as e:
                print(f"Error deleting file {filename}: {e}")

    if deleted_files_count == 0:
        print("No static files to delete")
        return 0

    return deleted_files_count


def main():
    print(f"Starting cleanup of static cache files at {datetime.now(UTC)}")

    css_folder = os.path.join(STATIC_ROOT, "CACHE", "css")
    js_folder = os.path.join(STATIC_ROOT, "CACHE", "js")

    print(f"\nProcessing CSS files in {css_folder}")
    css_deleted = delete_static_files(css_folder, "css")

    print(f"\nProcessing JS files in {js_folder}")
    js_deleted = delete_static_files(js_folder, "js")

    deleted_files_total = css_deleted + js_deleted

    print("\nSummary:")
    print(f"- CSS files deleted: {css_deleted}")
    print(f"- JS files deleted: {js_deleted}")
    print(f"- Total deleted static files: {deleted_files_total}")
    print(f"\nCleanup completed at {datetime.now(UTC)}")


if __name__ == "__main__":
    main()
