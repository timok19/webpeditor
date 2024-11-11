"""
This type stub file was generated by pyright.
"""

from typing import Any, Callable, List, Optional
from django.apps import AppConfig
from django.http import HttpRequest
from django.urls import URLResolver
from injector import Binder, Injector, Module, Provider, ThreadLocalScope

__version__ = ...
__all__ = ["RequestScope", "request"]
logger = ...

class DjangoInjectorConfig(AppConfig):
    name: str = ...
    injector: Injector = ...
    django_module: DjangoModule = ...

    def ready(self) -> None: ...

def inject_request_middleware(get_response: Callable) -> Callable: ...
def DjangoInjectorMiddleware(get_response: Callable) -> Callable: ...
def check_existing_csrf_exempt(fun: Callable, wrapper: Callable) -> Callable: ...
def wrap_function(fun: Callable, injector: Injector) -> Callable: ...
def wrap_drf_view_set(fun: Callable, injector: Injector) -> Callable: ...
def wrap_class_based_view(fun: Callable, injector: Injector) -> Callable: ...
def instance_method_wrapper(im: Callable) -> Callable: ...
def wrap_fun(fun: Callable, injector: Injector) -> Callable: ...
def process_resolver(resolver: URLResolver, injector: Injector) -> None: ...
def patch_command_loader(injector: Injector) -> None:
    """Patches the management command loader to allow injection into management commands."""
    ...

def process_list(lst: List, injector: Injector) -> List: ...

class RequestScope(ThreadLocalScope):
    """A scope whose object lifetime is tied to a request."""

    def get(self, key: Any, provider: Provider) -> Any: ...

request = ...

class DjangoModule(Module):
    def __init__(self, request_scope_class: type = ...) -> None: ...
    def set_request(self, request: HttpRequest) -> None: ...
    def get_request(self) -> Optional[HttpRequest]: ...
    def configure(self, binder: Binder) -> None: ...