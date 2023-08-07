import re


def replace_with_underscore(file_name: str) -> str:
    pattern = re.compile(r"[\s!@#%$&^*/{}\[\]+<>,?;:`~]+")
    new_file_name = re.sub(pattern, "_", file_name)

    return new_file_name
