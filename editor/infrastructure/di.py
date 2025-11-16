from anydi import Module, provider

from editor.infrastructure.abc.editor_repository_abc import EditorRepositoryABC
from editor.infrastructure.editor_repository import EditorRepository


class InfrastructureModule(Module):
    @provider(scope="request")
    def provide_editor_queries(self) -> EditorRepositoryABC:
        return EditorRepository()
