"""
This type stub file was generated by pyright.
"""

from django_otp.models import Device, ThrottlingMixin, TimestampMixin

def default_key():  # -> str:
    ...
def key_validator(value):  # -> None:
    ...

class TOTPDevice(TimestampMixin, ThrottlingMixin, Device):
    """
    A generic TOTP :class:`~django_otp.models.Device`. The model fields mostly
    correspond to the arguments to :func:`django_otp.oath.totp`. They all have
    sensible defaults, including the key, which is randomly generated.

    .. attribute:: key

        *CharField*: A hex-encoded secret key of up to 40 bytes. (Default: 20
        random bytes)

    .. attribute:: step

        *PositiveSmallIntegerField*: The time step in seconds. (Default: 30)

    .. attribute:: t0

        *BigIntegerField*: The Unix time at which to begin counting steps.
        (Default: 0)

    .. attribute:: digits

        *PositiveSmallIntegerField*: The number of digits to expect in a token
        (6 or 8).  (Default: 6)

    .. attribute:: tolerance

        *PositiveSmallIntegerField*: The number of time steps in the past or
        future to allow. For example, if this is 1, we'll accept any of three
        tokens: the current one, the previous one, and the next one. (Default:
        1)

    .. attribute:: drift

        *SmallIntegerField*: The number of time steps the prover is known to
        deviate from our clock.  If :setting:`OTP_TOTP_SYNC` is ``True``, we'll
        update this any time we match a token that is not the current one.
        (Default: 0)

    .. attribute:: last_t

        *BigIntegerField*: The time step of the last verified token. To avoid
        verifying the same token twice, this will be updated on each successful
        verification. Only tokens at a higher time step will be verified
        subsequently. (Default: -1)

    """

    key = ...
    step = ...
    t0 = ...
    digits = ...
    tolerance = ...
    drift = ...
    last_t = ...
    class Meta(Device.Meta):
        verbose_name = ...

    @property
    def bin_key(self):  # -> bytes:
        """
        The secret key as a binary string.
        """
        ...

    def verify_token(self, token):  # -> bool:
        ...
    def get_throttle_factor(self):  # -> Any | int:
        ...
    @property
    def config_url(self):  # -> str:
        """
        A URL for configuring Google Authenticator or similar.

        See https://github.com/google/google-authenticator/wiki/Key-Uri-Format.
        The issuer is taken from :setting:`OTP_TOTP_ISSUER`, if available.
        The image (for e.g. FreeOTP) is taken from :setting:`OTP_TOTP_IMAGE`, if available.

        """
        ...
