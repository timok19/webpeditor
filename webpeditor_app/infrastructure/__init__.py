from anydi import Module, provider

from webpeditor_app.infrastructure.abc.converter_queries_abc import ConverterQueriesABC
from webpeditor_app.infrastructure.abc.editor_queries_abc import EditorQueriesABC
from webpeditor_app.infrastructure.cloudinary.cloudinary_client import CloudinaryClient
from webpeditor_app.infrastructure.database.converter_queries import ConverterQueries
from webpeditor_app.infrastructure.database.editor_queries import EditorQueries


class InfrastructureModule(Module):
    @provider(scope="singleton")
    def provide_cloudinary_client(self) -> CloudinaryClient:
        return CloudinaryClient()

    @provider(scope="request")
    def provide_converter_queries(self) -> ConverterQueriesABC:
        return ConverterQueries()

    @provider(scope="request")
    def provide_editor_queries(self) -> EditorQueriesABC:
        return EditorQueries()
