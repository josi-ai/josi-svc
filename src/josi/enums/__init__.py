"""Josi enums — all inherit from BaseEnum with (id, description) pattern."""
from josi.enums.base_enum import BaseEnum
from josi.enums.subscription_tier_enum import SubscriptionTierEnum
from josi.enums.astrology_system_enum import AstrologySystemEnum
from josi.enums.house_system_enum import HouseSystemEnum
from josi.enums.ayanamsa_enum import AyanamsaEnum
from josi.enums.consultation_status_enum import ConsultationStatusEnum
from josi.enums.consultation_type_enum import ConsultationTypeEnum
from josi.enums.payment_status_enum import PaymentStatusEnum
from josi.enums.astrologer_specialization_enum import AstrologerSpecializationEnum
from josi.enums.verification_status_enum import VerificationStatusEnum
from josi.enums.remedy_type_enum import RemedyTypeEnum
from josi.enums.tradition_enum import TraditionEnum
from josi.enums.dosha_type_enum import DoshaTypeEnum
from josi.enums.interpretation_style_enum import InterpretationStyleEnum
from josi.enums.ai_provider_enum import AIProviderEnum
from josi.enums.error_code_enum import ErrorCodeEnum

ALL_ENUMS = {
    "subscription_tiers": SubscriptionTierEnum,
    "astrology_systems": AstrologySystemEnum,
    "house_systems": HouseSystemEnum,
    "ayanamsas": AyanamsaEnum,
    "consultation_statuses": ConsultationStatusEnum,
    "consultation_types": ConsultationTypeEnum,
    "payment_statuses": PaymentStatusEnum,
    "astrologer_specializations": AstrologerSpecializationEnum,
    "verification_statuses": VerificationStatusEnum,
    "remedy_types": RemedyTypeEnum,
    "traditions": TraditionEnum,
    "dosha_types": DoshaTypeEnum,
    "interpretation_styles": InterpretationStyleEnum,
    "ai_providers": AIProviderEnum,
    "error_codes": ErrorCodeEnum,
}
