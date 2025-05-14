from typing import Any, Optional

from returns.pipeline import is_successful

from webpeditor_app.common import ValueResult
from webpeditor_app.models import ConverterImageAsset
from webpeditor_app.application.auth import SessionService


class ConvertedImagesDestroyAPIView:
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(csrf_protect)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        session_service: SessionService = self.__session_service_factory.create(request)
        signed_user_id_result: ValueResult[str] = session_service.aget_user_id()

        if not is_successful(signed_user_id_result):
            return ResultResponse.from_error(signed_user_id_result.failure2())

        signed_user_id: str = signed_user_id_result.unwrap()

        unsigned_user_id_result: ValueResult[str] = self.__user_service.unsign_id(signed_user_id)

        if not is_successful(unsigned_user_id_result):
            return ResultResponse.from_error(unsigned_user_id_result.failure2())

        unsigned_user_id: str = unsigned_user_id_result.unwrap()

        converted_image_asset: Optional[ConverterImageAsset] = (
            self.get_queryset()
            .filter(
                user_id=unsigned_user_id,
                id=kwargs["pk"],
            )
            .first()
        )

        # if converted_image_asset is None:
        #     return ResultResponse.failure(message="Converted image asset not found", status_code=status.HTTP_404_NOT_FOUND)

        # TODO: finish the implementation (take logic from remaining apis)

        session_service.aasynchronize()

        return super().destroy(request, *args, **kwargs)
