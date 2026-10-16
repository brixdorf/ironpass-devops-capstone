from enum import Enum


class PlanType(str, Enum):
    """Kind of plan. The values are exact capital letters."""

    DAY_PASS = "DAY_PASS"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"


class MemberStatus(str, Enum):
    """Status of a member.

    ACTIVE, FROZEN and CANCELLED are stored in the database.
    EXPIRED is worked out from the expiry date, it is never stored.
    """

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    FROZEN = "FROZEN"
    CANCELLED = "CANCELLED"


class StoredStatus(str, Enum):
    """The statuses staff are allowed to set by hand."""

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CANCELLED = "CANCELLED"


class ActivityType(str, Enum):
    CHECKIN = "CHECKIN"
    SIGNUP = "SIGNUP"
