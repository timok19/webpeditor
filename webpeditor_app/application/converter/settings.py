from typing import ClassVar, final


@final
class ConverterSettings:
    MIN_QUALITY: ClassVar[int] = 5
    MAX_QUALITY: ClassVar[int] = 100
    MAX_FILE_SIZE: ClassVar[int] = 6_291_456
    MAX_FILES_LIMIT: ClassVar[int] = 10
