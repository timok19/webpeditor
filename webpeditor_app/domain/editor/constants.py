from typing import final, Final

from webpeditor_app.domain.common.constants import ImagePropertyConstants


@final
class ImageEditorConstants(ImagePropertyConstants):
    MAX_FILE_SIZE: Final[int] = 6_291_456
