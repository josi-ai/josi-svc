from josi.enums.base_enum import BaseEnum


class PaymentStatusEnum(BaseEnum):
    PENDING = (1, "Pending")
    PAID = (2, "Paid")
    FAILED = (3, "Failed")
    REFUNDED = (4, "Refunded")
    PARTIALLY_REFUNDED = (5, "Partially Refunded")
