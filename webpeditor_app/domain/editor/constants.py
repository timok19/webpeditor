from typing import final, Final

from webpeditor_app.domain.common.constants import ImageFilePropertyConstants


@final
class ImageEditorConstants(ImageFilePropertyConstants):
    MAX_FILE_SIZE: Final[int] = 6_291_456
