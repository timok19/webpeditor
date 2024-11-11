import os
import time

from webpeditor.settings import STATIC_ROOT


def delete_old_css_files(path_to_css: str) -> None:
    files: list[str] = os.listdir(path_to_css)

    deleted_files_count: int = 0

    for file in files:
        file_path: str = os.path.join(path_to_css, file)

        file_name, file_extension = os.path.splitext(file)

        if not os.path.isfile(file_path) and not file_extension.__contains__(".css"):
            print("There is no css file to delete")
            break

        creation_time: float = os.path.getctime(file_path)

        if time.time() - creation_time > 86400:
            os.remove(file_path)
            deleted_files_count += 1
            print(f"Deleted file: {file_name}{file_extension}")

    print(f"Total deleted CSS files: {deleted_files_count}")


if __name__ == "__main__":
    delete_old_css_files(os.path.join(STATIC_ROOT, "CACHE", "css"))
