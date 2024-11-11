from dataclasses import dataclass


# TODO: Adjust UploadOptions to match the requirements of Cloudinary service (make typesafe)
@dataclass(frozen=True)
class UploadOptions:
    folder_path: str
    use_filename: bool
    unique_filename: bool
    filename_override: str
    overwrite: bool
