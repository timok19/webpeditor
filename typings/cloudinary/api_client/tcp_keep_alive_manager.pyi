"""
This type stub file was generated by pyright.
"""

from urllib3 import HTTPConnectionPool, HTTPSConnectionPool, PoolManager, ProxyManager

TCP_KEEPALIVE = ...
TCP_KEEP_IDLE = ...
TCP_KEEPALIVE_INTERVAL = ...
TCP_KEEP_CNT = ...

class TCPKeepAliveValidationMethods:
    """
    This class contains a single method whose sole purpose is to set up TCP Keep Alive probes on the socket for a
    connection. This is necessary for long-running requests which will be silently terminated by the AWS Network Load
    Balancer which kills a connection if it is idle for more than 350 seconds.
    """
    @staticmethod
    def adjust_connection_socket(conn, protocol=...):  # -> None:
        """
        Adjusts the socket settings so that the client sends a TCP keep alive probe over the connection. This is only
        applied where possible, if the ability to set the socket options is not available, for example using Anaconda,
        then the settings will be left as is.
        :param conn: The connection to update the socket settings for
        :param str protocol: The protocol of the connection
        :return: None
        """
        ...

class TCPKeepAliveHTTPSConnectionPool(HTTPSConnectionPool):
    """
    This class overrides the _validate_conn method in the HTTPSConnectionPool class. This is the entry point to use
    for modifying the socket as it is called after the socket is created and before the request is made.
    """

    ...

class TCPKeepAliveHTTPConnectionPool(HTTPConnectionPool):
    """
    This class overrides the _validate_conn method in the HTTPSConnectionPool class. This is the entry point to use
    for modifying the socket as it is called after the socket is created and before the request is made.
    In the base class this method is passed completely.
    """

    ...

class TCPKeepAlivePoolManager(PoolManager):
    """
    This Pool Manager has only had the pool_classes_by_scheme variable changed. This now points at the TCPKeepAlive
    connection pools rather than the default connection pools.
    """
    def __init__(self, num_pools=..., headers=..., **connection_pool_kw) -> None: ...

class TCPKeepAliveProxyManager(ProxyManager):
    """
    This Proxy Manager has only had the pool_classes_by_scheme variable changed. This now points at the TCPKeepAlive
    connection pools rather than the default connection pools.
    """
    def __init__(self, proxy_url, num_pools=..., headers=..., proxy_headers=..., **connection_pool_kw) -> None: ...