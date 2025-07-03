from names_generator import generate_name
from uuid_utils import uuid7


def generate_id() -> str:
    return f"{generate_name(style='hyphen')}-{uuid7()}"
