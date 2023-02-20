from localStoragePy import localStoragePy


def initialize_local_storage():
    return localStoragePy("webpeditor_app", "json")


def check_before_save_to_local_storage(local_storage: localStoragePy, uploaded_image_url: str):
    local_storage.setItem("image_url", f"{uploaded_image_url}")
    if local_storage.getItem("image_url") is not None:
        print("Image saved to local_storage successfully")
    else:
        print("Something went wrong. Image did not save to local_storage")


def save_to_local_storage(local_storage: localStoragePy, uploaded_image_url: str):
    if local_storage.getItem("image_url") is not None:
        local_storage.removeItem("image_url")
        check_before_save_to_local_storage(local_storage, uploaded_image_url)
    else:
        check_before_save_to_local_storage(local_storage, uploaded_image_url)
