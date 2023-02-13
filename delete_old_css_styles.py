import os
import time

from webpeditor.settings import STATIC_ROOT


def delete_old_css_styles(path_to_css: str):
    files = os.listdir(path_to_css)

    for file in files:
        file_path = os.path.join(path_to_css, file)

        file_name, file_extension = os.path.splitext(file)

        if not os.path.isfile(file_path) and not file_extension == '.css':
            print("There is no css file to delete")
            break

        creation_time = os.path.getctime(file_path)

        if time.time() - creation_time > 86400:
            os.remove(file_path)
            print(f"Deleted file: {file_name}{file_extension}")
        else:
            print("There is no css file which is older than one day :)")
            break


delete_old_css_styles(f"{STATIC_ROOT}/CACHE/css/")
