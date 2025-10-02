from typing import final, Final

from webpeditor_app.domain.common.constants import ImagePropertyConstants


@final
class ImageConverterConstants(ImagePropertyConstants):
    MIN_QUALITY: Final[int] = 5
    MAX_QUALITY: Final[int] = 100
    MAX_FILE_SIZE: Final[int] = 6_291_456
    MAX_FILES_LIMIT: Final[int] = 10
    MAX_IMAGE_DIMENSIONS: Final[int] = 4000
    SAFE_AREA: Final[int] = 1_000_000
    
