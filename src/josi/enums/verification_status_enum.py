from josi.enums.base_enum import BaseEnum


class VerificationStatusEnum(BaseEnum):
    PENDING = (1, "Pending")
    VERIFIED = (2, "Verified")
    REJECTED = (3, "Rejected")
    SUSPENDED = (4, "Suspended")
