from typing import ClassVar, final


@final
class ConverterConstants:
    MIN_QUALITY: ClassVar[int] = 5
    MAX_QUALITY: ClassVar[int] = 100
    MAX_FILE_SIZE: ClassVar[int] = 6_291_456
    MAX_FILES_LIMIT: ClassVar[int] = 10
    MAX_IMAGE_DIMENSIONS: ClassVar[int] = 4000
    SAFE_AREA: ClassVar[int] = 1_000_000
