"""
This type stub file was generated by pyright.
"""

from time import time

def hotp(key, counter, digits=...):  # -> Any:
    """
    Implementation of the HOTP algorithm from `RFC 4226
    <http://tools.ietf.org/html/rfc4226#section-5>`_.

    :param bytes key: The shared secret. A 20-byte string is recommended.
    :param int counter: The password counter.
    :param int digits: The number of decimal digits to generate.

    :returns: The HOTP token.
    :rtype: int

    >>> key = b'12345678901234567890'
    >>> for c in range(10):
    ...     hotp(key, c)
    755224
    287082
    359152
    969429
    338314
    254676
    287922
    162583
    399871
    520489
    """
    ...

def totp(key, step=..., t0=..., digits=..., drift=...):  # -> Any:
    """
    Implementation of the TOTP algorithm from `RFC 6238
    <http://tools.ietf.org/html/rfc6238#section-4>`_.

    :param bytes key: The shared secret. A 20-byte string is recommended.
    :param int step: The time step in seconds. The time-based code changes
        every ``step`` seconds.
    :param int t0: The Unix time at which to start counting time steps.
    :param int digits: The number of decimal digits to generate.
    :param int drift: The number of time steps to add or remove. Delays and
        clock differences might mean that you have to look back or forward a
        step or two in order to match a token.

    :returns: The TOTP token.
    :rtype: int

    >>> key = b'12345678901234567890'
    >>> now = int(time())
    >>> for delta in range(0, 200, 20):
    ...     totp(key, t0=(now-delta))
    755224
    755224
    287082
    359152
    359152
    969429
    338314
    338314
    254676
    287922
    """
    ...

class TOTP:
    """
    An alternate TOTP interface.

    This provides access to intermediate steps of the computation. This is a
    living object: the return values of ``t`` and ``token`` will change along
    with other properties and with the passage of time.

    :param bytes key: The shared secret. A 20-byte string is recommended.
    :param int step: The time step in seconds. The time-based code changes
        every ``step`` seconds.
    :param int t0: The Unix time at which to start counting time steps.
    :param int digits: The number of decimal digits to generate.
    :param int drift: The number of time steps to add or remove. Delays and
        clock differences might mean that you have to look back or forward a
        step or two in order to match a token.

    >>> key = b'12345678901234567890'
    >>> totp = TOTP(key)
    >>> totp.time = 0
    >>> totp.t()
    0
    >>> totp.token()
    755224
    >>> totp.time = 30
    >>> totp.t()
    1
    >>> totp.token()
    287082
    >>> totp.verify(287082)
    True
    >>> totp.verify(359152)
    False
    >>> totp.verify(359152, tolerance=1)
    True
    >>> totp.drift
    1
    >>> totp.drift = 0
    >>> totp.verify(359152, tolerance=1, min_t=3)
    False
    >>> totp.drift
    0
    >>> del totp.time
    >>> totp.t0 = int(time()) - 60
    >>> totp.t()
    2
    >>> totp.token()
    359152
    """
    def __init__(self, key, step=..., t0=..., digits=..., drift=...) -> None: ...
    def token(self):  # -> Any:
        """The computed TOTP token."""
        ...

    def t(self):  # -> int:
        """The computed time step."""
        ...

    @property
    def time(self):  # -> float:
        """
        The current time.

        By default, this returns time.time() each time it is accessed. If you
        want to generate a token at a specific time, you can set this property
        to a fixed value instead. Deleting the value returns it to its 'live'
        state.

        """
        ...

    @time.setter
    def time(self, value):  # -> None:
        ...
    @time.deleter
    def time(self):  # -> None:
        ...
    def verify(self, token, tolerance=..., min_t=...):  # -> bool:
        """
        A high-level verification helper.

        :param int token: The provided token.
        :param int tolerance: The amount of clock drift you're willing to
            accommodate, in steps. We'll look for the token at t values in
            [t - tolerance, t + tolerance].
        :param int min_t: The minimum t value we'll accept. As a rule, this
            should be one larger than the largest t value of any previously
            accepted token.
        :rtype: bool

        Iff this returns True, `self.drift` will be updated to reflect the
        drift value that was necessary to match the token.

        """
        ...
