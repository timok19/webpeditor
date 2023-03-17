import re


def replace_with_underscore(file_name: str) -> str:
    # Define the pattern for spaces and special characters
    pattern = re.compile(r'[\s!@#%$&^*/{}\[\]+<>,?;:`~]+')

    # Replace spaces and special characters with an underscore character
    file_name = re.sub(pattern, '_', file_name)

    return file_name
