"""
This type stub file was generated by pyright.
"""

from cloudinary.utils import check_property_enabled

class ResponsiveBreakpointsCache:
    """
    Caches breakpoint values for image resources
    """
    def __init__(self, **cache_options) -> None:
        """
        Initialize the cache

        :param cache_options: Cache configuration options
        """
        ...

    def set_cache_adapter(self, cache_adapter):  # -> bool:
        """
        Assigns cache adapter

        :param cache_adapter: The cache adapter used to store and retrieve values

        :return: Returns True if the cache_adapter is valid
        """
        ...

    @property
    def enabled(self):  # -> bool:
        """
        Indicates whether cache is enabled or not

        :return: Rrue if a _cache_adapter has been set
        """
        ...

    @check_property_enabled
    def get(self, public_id, **options):
        """
        Retrieve the breakpoints of a particular derived resource identified by the public_id and options

        :param public_id: The public ID of the resource
        :param options: The public ID of the resource

        :return: Array of responsive breakpoints, None if not found
        """
        ...

    @check_property_enabled
    def set(self, public_id, value, **options):
        """
        Set responsive breakpoints identified by public ID and options

        :param public_id: The public ID of the resource
        :param value:  Array of responsive breakpoints to set
        :param options: Additional options

        :return: True on success or False on failure
        """
        ...

    @check_property_enabled
    def delete(self, public_id, **options):
        """
        Delete responsive breakpoints identified by public ID and options

        :param public_id: The public ID of the resource
        :param options: Additional options

        :return: True on success or False on failure
        """
        ...

    @check_property_enabled
    def flush_all(self):
        """
        Flush all entries from cache

        :return: True on success or False on failure
        """
        ...

instance = ...
