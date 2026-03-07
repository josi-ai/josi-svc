from josi.enums.base_enum import BaseEnum


class ConsultationStatusEnum(BaseEnum):
    PENDING = (1, "Pending")
    SCHEDULED = (2, "Scheduled")
    IN_PROGRESS = (3, "In Progress")
    COMPLETED = (4, "Completed")
    CANCELLED = (5, "Cancelled")
    REFUNDED = (6, "Refunded")
