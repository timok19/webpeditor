from datetime import timedelta
from typing import Any, Optional

from django.core.handlers.wsgi import WSGIRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from injector import inject
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from webpeditor_app.common.responses.resultant_response import ResultantResponse
from webpeditor_app.common.resultant import Resultant, ResultantValue, ErrorCode
from webpeditor_app.models import ConvertedImageAsset
from webpeditor_app.serializers import ConvertedImageSerializer
from webpeditor_app.core.auth.session.session_service import SessionService
from webpeditor_app.core.auth.session.session_service_factory_abc import SessionServiceFactoryABC
from webpeditor_app.core.auth.user.user_service_abc import UserServiceABC


class ConvertedImageCreateAPIView(ListCreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = ConvertedImageSerializer
    queryset = ConvertedImageAsset.objects.all()
    __session_service_factory: SessionServiceFactoryABC

    @inject
    def setup(
        self,
        request: WSGIRequest,
        session_service_factory: SessionServiceFactoryABC,
        **kwargs: Any,
    ) -> None:
        super().setup(request, **kwargs)
        self.__session_service_factory = session_service_factory

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(csrf_protect)
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        session_service: SessionService = self.__session_service_factory.create(request)
        session_service.add_or_get_signed_user_id()
        session_service.set_session_expiry(timedelta(minutes=15))

        # converted_images = run_conversion_task(
        #     str(user_id),
        #     request,
        #     cast(typ=list[InMemoryUploadedFile], val=image_files),
        #     int(str(quality)),
        #     str(output_format),
        # )

        # request.session.pop("error_message", None)
        # request.session.pop("converted_images", None)
        # request.session["converted_images"] = []

        session_service.update_session_store()

        return super().post(request, *args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(csrf_protect)
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)


class ConvertedImageDeleteAPIView(DestroyAPIView):
    serializer_class = ConvertedImageSerializer
    queryset = ConvertedImageAsset.objects.all()
    __session_service_factory: SessionServiceFactoryABC
    __user_service: UserServiceABC

    @inject
    def setup(
        self,
        request: WSGIRequest,
        session_service_factory: SessionServiceFactoryABC,
        user_service: UserServiceABC,
        **kwargs: Any,
    ) -> None:
        super().setup(request, **kwargs)
        self.__session_service_factory = session_service_factory
        self.__user_service = user_service

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(csrf_protect)
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        session_service: SessionService = self.__session_service_factory.create(request)
        signed_user_id_resultant: ResultantValue[str] = session_service.get_signed_user_id()

        if not Resultant.is_successful(signed_user_id_resultant):
            return ResultantResponse.from_resultant(signed_user_id_resultant)

        signed_user_id: str = signed_user_id_resultant.unwrap()

        unsigned_user_id_resultant: ResultantValue[str] = self.__user_service.unsign_user_id(signed_user_id)

        if not Resultant.is_successful(unsigned_user_id_resultant):
            return ResultantResponse.from_resultant(unsigned_user_id_resultant)

        unsigned_user_id: str = unsigned_user_id_resultant.unwrap()

        converted_image_asset: Optional[ConvertedImageAsset] = ConvertedImageAsset.objects.filter(user_id=unsigned_user_id).first()

        if converted_image_asset is None:
            return ResultantResponse.error(message="Converted image not found", error_code=ErrorCode.NOT_FOUND)

        # TODO: finish the implementation (take logic from remaining apis)

        session_service.update_session_store()

        return super().destroy(request, *args, **kwargs)
