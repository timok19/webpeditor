from typing import cast, Type

from django.apps import apps
from django_injector.apps import DjangoInjectorConfig
from injector import ScopeDecorator, Scope


def get_dependency[T: object](interface: Type[T], *, scope: ScopeDecorator | type[Scope] | None = None) -> T:
    injector_config: DjangoInjectorConfig = cast(DjangoInjectorConfig, apps.get_app_config(DjangoInjectorConfig.name))

    return injector_config.injector.get(interface, scope)
