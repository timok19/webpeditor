# from anydi_django import container
from django_extensions.management.jobs import DailyJob


class CleanupJob(DailyJob):
    help = "Clean up expired users data"

    def __init__(self) -> None:
        # TODO: inject necessary services and implement the cleanup mechanism
        # container.resolve()
        ...

    def execute(self) -> None:
        raise NotImplementedError()
