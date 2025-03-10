"""
This type stub file was generated by pyright.
"""

import enum
from django.db import models
from django.utils.functional import cached_property

class DeviceManager(models.Manager):
    """
    The :class:`~django.db.models.Manager` object installed as
    ``Device.objects``.
    """
    def devices_for_user(self, user, confirmed=...):
        """
        Returns a queryset for all devices of this class that belong to the
        given user.

        :param user: The user.
        :type user: :class:`~django.contrib.auth.models.User`

        :param confirmed: If ``None``, all matching devices are returned.
            Otherwise, this can be any true or false value to limit the query
            to confirmed or unconfirmed devices, respectively.

        """
        ...

class Device(models.Model):
    """
    Abstract base model for a :term:`device` attached to a user. Plugins must
    subclass this to define their OTP models.

    .. _unsaved_device_warning:

    .. warning::

        OTP devices are inherently stateful. For example, verifying a token is
        logically a mutating operation on the device, which may involve
        incrementing a counter or otherwise consuming a token. A device must be
        committed to the database before it can be used in any way.

    .. attribute:: user

        *ForeignKey*: Foreign key to your user model, as configured by
        :setting:`AUTH_USER_MODEL` (:class:`~django.contrib.auth.models.User`
        by default).

    .. attribute:: name

        *CharField*: A human-readable name to help the user identify their
        devices.

    .. attribute:: confirmed

        *BooleanField*: A boolean value that tells us whether this device has
        been confirmed as valid. It defaults to ``True``, but subclasses or
        individual deployments can force it to ``False`` if they wish to create
        a device and then ask the user for confirmation. As a rule, built-in
        APIs that enumerate devices will only include those that are confirmed.

    .. attribute:: objects

        A :class:`~django_otp.models.DeviceManager`.

    """

    user = ...
    name = ...
    confirmed = ...
    objects = ...
    class Meta:
        abstract = ...

    def __str__(self) -> str: ...
    @property
    def persistent_id(self):  # -> str:
        """
        A stable device identifier for forms and APIs.
        """
        ...

    @classmethod
    def model_label(cls):  # -> str:
        """
        Returns an identifier for this Django model class.

        This is just the standard "<app_label>.<model_name>" form.

        """
        ...

    @classmethod
    def from_persistent_id(cls, persistent_id, for_verify=...):  # -> Device | None:
        """
        Loads a device from its persistent id::

            device == Device.from_persistent_id(device.persistent_id)

        :param bool for_verify: If ``True``, we'll load the device with
            :meth:`~django.db.models.query.QuerySet.select_for_update` to
            prevent concurrent verifications from succeeding. In which case,
            this must be called inside a transaction.

        """
        ...

    def is_interactive(self):  # -> bool:
        """
        Returns ``True`` if this is an interactive device.

        The default implementation returns ``True`` if
        :meth:`~django_otp.models.Device.generate_challenge` has been
        overridden, but subclasses are welcome to provide smarter
        implementations.

        :rtype: bool

        """
        ...

    def generate_is_allowed(self):  # -> tuple[Literal[True], None]:
        """
        Checks whether it is permissible to call :meth:`generate_challenge`.

        If it is allowed, returns ``(True, None)``. Otherwise returns ``(False,
        data_dict)``, where ``data_dict`` contains extra information, defined
        by the implementation.

        This method can be used to implement throttling of token generation for
        interactive devices. Client code should check this method before
        calling :meth:`generate_challenge` and report problems to the user.

        """
        ...

    def generate_challenge(self):  # -> None:
        """
        Generates a challenge value that the user will need to produce a token.

        This method is permitted to have side effects, such as transmitting
        information to the user through some other channel (email or SMS,
        perhaps). And, of course, some devices may need to commit the challenge
        to the database.

        :returns: A message to the user. This should be a string that fits
            comfortably in the template ``'OTP Challenge: {0}'``. This may
            return ``None`` if this device is not interactive.
        :rtype: string or ``None``

        :raises: Any :exc:`~exceptions.Exception` is permitted. Callers should
            trap ``Exception`` and report it to the user.

        """
        ...

    def verify_is_allowed(self):  # -> tuple[Literal[True], None]:
        """
        Checks whether it is permissible to call :meth:`verify_token`.

        If it is allowed, returns ``(True, None)``. Otherwise returns ``(False,
        data_dict)``, where ``data_dict`` contains extra information, defined
        by the implementation.

        This method can be used to implement throttling or locking, for
        example. Client code should check this method before calling
        :meth:`verify_token` and report problems to the user.

        To report specific problems, the data dictionary can return include a
        ``'reason'`` member with a value from the constants in
        :class:`VerifyNotAllowed`. Otherwise, an ``'error_message'`` member
        should be provided with an error message.

        :meth:`verify_token` should also call this method and return False if
        verification is not allowed.

        :rtype: (bool, dict or ``None``)

        """
        ...

    def verify_token(self, token):  # -> Literal[False]:
        """
        Verifies a token.

        As a rule, the token should no longer be valid if this returns
        ``True``.

        :param str token: The OTP token provided by the user.
        :rtype: bool

        """
        ...

class SideChannelDevice(Device):
    """
    Abstract base model for a side-channel :term:`device` attached to a user.

    This model implements token generation, verification and expiration, so the
    concrete devices only have to implement delivery.

    .. attribute:: token

        The token most recently generated for the user.

    .. attribute:: valid_until

        The datetime at which the stored token will expire.

    """

    token = ...
    valid_until = ...
    class Meta:
        abstract = ...

    def generate_token(self, length=..., valid_secs=..., commit=...):  # -> None:
        """
        Generates a token of the specified length, then sets it on the model
        and sets the expiration of the token on the model.

        :param int length: Number of decimal digits in the generated token.
        :param int valid_secs: Amount of seconds the token should be valid.
        :param bool commit: Pass False if you intend to save the instance
            yourself.

        """
        ...

    def verify_token(self, token):  # -> bool:
        """
        Verifies a token by content and expiry.

        On success, the token is cleared and the device saved.

        :param str token: The OTP token provided by the user.
        :rtype: bool

        """
        ...

class GenerateNotAllowed(enum.Enum):
    """
    Constants that may be returned in the ``reason`` member of the extra
    information dictionary returned by
    :meth:`~django_otp.models.Device.generate_is_allowed`.

    .. data:: COOLDOWN_DURATION_PENDING

       Indicates that a token was generated recently and we're waiting for the
       cooldown period to expire.

    """

    COOLDOWN_DURATION_PENDING = ...

class CooldownMixin(models.Model):
    """
    Mixin class for models requiring a cooldown duration between challenge
    generations.

    Subclass must implement :meth:`get_cooldown_duration`, and must use the
    :meth:`generate_is_allowed` method from within their generate_challenge()
    method. Further it must use :meth:`cooldown_set` when a token is generated.

    See the implementation of
    :class:`~django_otp.plugins.otp_email.models.EmailDevice` for an example.

    .. attribute:: last_generated_timestamp

        The last time a token was generated for this device.

    """

    last_generated_timestamp = ...
    class Meta:
        abstract = ...

    def generate_is_allowed(self):  # -> tuple[Literal[False], dict[str, Any]]:
        """
        If token generation is allowed, returns ``(True, None)``. Otherwise,
        returns ``(False, data_dict)``.

        ``data_dict`` contains further information. Currently it can be::

            {
                'reason': GenerateNotAllowed.COOLDOWN_DURATION_PENDING,
                'next_generation_at': when,
            }

        where ``when`` is a datetime marking the end of the cooldown period.
        See :class:`GenerateNotAllowed`.

        """
        ...

    def cooldown_reset(self, commit=...):  # -> None:
        """
        Call this method to reset cooldown (normally after a successful
        verification).

        :param bool commit: Pass False if you intend to save the instance
            yourself.

        """
        ...

    def cooldown_set(self, commit=...):  # -> None:
        """
        Call this method to set the cooldown timestamp to now (normally when
        a token is generated).

        :param bool commit: Pass False if you intend to save the instance
            yourself.

        """
        ...

    def verify_token(self, token):
        """
        Reset the throttle if the token is valid.
        """
        ...

    @cached_property
    def cooldown_enabled(self): ...
    def get_cooldown_duration(self):
        """
        This must be implemented to return the cooldown duration in seconds.

        A duration of 0 disables the cooldown.

        Normally this is just a wrapper for a plugin-specific setting like
        :setting:`OTP_EMAIL_COOLDOWN_DURATION`.

        """
        ...

class VerifyNotAllowed(enum.Enum):
    """
    Constants that may be returned in the ``reason`` member of the extra
    information dictionary returned by
    :meth:`~django_otp.models.Device.verify_is_allowed`

    .. data:: N_FAILED_ATTEMPTS

       Indicates that verification is disallowed because of ``n`` successive
       failed attempts. The data dictionary should include the value of ``n``
       in member ``failure_count``

    """

    N_FAILED_ATTEMPTS = ...

class ThrottlingMixin(models.Model):
    """
    Mixin class for models that want throttling behaviour.

    This implements exponential back-off for verifying tokens. Subclasses must
    implement :meth:`get_throttle_factor`, and must use the
    :meth:`verify_is_allowed`, :meth:`throttle_reset` and
    :meth:`throttle_increment` methods from within their verify_token() method.

    See the implementation of
    :class:`~django_otp.plugins.otp_email.models.EmailDevice` for an example.

    .. attribute:: throttling_failure_timestamp

        The datetime of the last failed verification attempt.

    .. attribute:: throttling_failure_count

        The number of consecutive failed verification attempts.

    """

    throttling_failure_timestamp = ...
    throttling_failure_count = ...
    class Meta:
        abstract = ...

    def verify_is_allowed(self):  # -> tuple[Literal[False], dict[str, Any]]:
        """
        If verification is allowed, returns ``(True, None)``.
        Otherwise, returns ``(False, data_dict)``.

        ``data_dict`` contains further information. Currently it can be::

            {
                'reason': VerifyNotAllowed.N_FAILED_ATTEMPTS,
                'failure_count': n
            }

        where ``n`` is the number of successive failures. See
        :class:`~django_otp.models.VerifyNotAllowed`.

        """
        ...

    def throttle_reset(self, commit=...):  # -> None:
        """
        Call this method to reset throttling (normally when a verify attempt
        succeeded).

        :param bool commit: Pass False if you intend to save the instance
            yourself.

        """
        ...

    def throttle_increment(self, commit=...):  # -> None:
        """
        Call this method to increase throttling (normally when a verify attempt
        failed).

        :param bool commit: Pass False if you intend to save the instance
            yourself.

        """
        ...

    @cached_property
    def throttling_enabled(self): ...
    def get_throttle_factor(self):
        """
        This must be implemented to return the throttle factor.

        The number of seconds required between verification attempts will be
        :math:`c2^{n-1}` where `c` is this factor and `n` is the number of
        previous failures. A factor of 1 translates to delays of 1, 2, 4, 8,
        etc. seconds. A factor of 0 disables the throttling.

        Normally this is just a wrapper for a plugin-specific setting like
        :setting:`OTP_EMAIL_THROTTLE_FACTOR`.

        """
        ...

class TimestampMixin(models.Model):
    """
    Mixin class that adds timestamps to devices.

    This mixin adds fields to record when a device was initially created in the
    system and when it was last used. It enhances the ability to audit device
    usage and lifecycle.

    Subclasses can use :meth:`set_last_used_timestamp` to update the
    `last_used_at` timestamp whenever the device is used for verification.

    .. attribute:: created_at

        The datetime at which this device was created.

    .. attribute:: last_used_at

        The datetime at which this device was last successfully used for
        verification.

    """

    created_at = ...
    last_used_at = ...
    class Meta:
        abstract = ...

    def set_last_used_timestamp(self, commit=...):  # -> None:
        """
        Updates the `last_used_at` field to the current datetime to indicate
        that the device has been used.

        :param bool commit: Pass False if you intend to save the instance
            yourself.

        """
        ...
