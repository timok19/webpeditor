from typing import Optional, override

from django.http import HttpRequest
from ninja_extra.throttling import SimpleRateThrottle


class _RateThrottleBase(SimpleRateThrottle):
    @override
    def get_cache_key(self, request: HttpRequest) -> Optional[str]:
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class Anonymous60MinutesRateThrottle(_RateThrottleBase):
    rate = "60/min"
    scope = "minutes"


class Anonymous100PerDayRateThrottle(_RateThrottleBase):
    rate = "100/day"
    scope = "days"


class Anonymous1000PerDayRateThrottle(_RateThrottleBase):
    rate = "1000/day"
    scope = "days"
