"""
This type stub file was generated by pyright.
"""

def hex_validator(length=...):  # -> Callable[..., None]:
    """
    Returns a function to be used as a model validator for a hex-encoded
    CharField. This is useful for secret keys of all kinds::

        def key_validator(value):
            return hex_validator(20)(value)

        key = models.CharField(max_length=40, validators=[key_validator], help_text='A hex-encoded 20-byte secret key')

    :param int length: If greater than 0, validation will fail unless the
        decoded value is exactly this number of bytes.

    :rtype: function

    >>> hex_validator()('0123456789abcdef')
    >>> hex_validator(8)(b'0123456789abcdef')
    >>> hex_validator()('phlebotinum')          # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValidationError: ['phlebotinum is not valid hex-encoded data.']
    >>> hex_validator(9)('0123456789abcdef')    # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValidationError: ['0123456789abcdef does not represent exactly 9 bytes.']
    """
    ...

def random_hex(length=...):  # -> str:
    """
    Returns a string of random bytes encoded as hex.

    This uses :func:`os.urandom`, so it should be suitable for generating
    cryptographic keys.

    :param int length: The number of (decoded) bytes to return.

    :returns: A string of hex digits.
    :rtype: str

    """
    ...

def random_number_token(length=...):  # -> str:
    """
    Returns a string of random digits encoded as string.

    :param int length: The number of digits to return.

    :returns: A string of decimal digits.
    :rtype: str

    """
    ...
