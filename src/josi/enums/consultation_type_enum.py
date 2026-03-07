from josi.enums.base_enum import BaseEnum


class ConsultationTypeEnum(BaseEnum):
    VIDEO = (1, "Video")
    CHAT = (2, "Chat")
    EMAIL = (3, "Email")
    VOICE = (4, "Voice")
