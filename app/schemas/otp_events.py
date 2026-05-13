from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.models.otp_event import OtpType


class SendOtpRequest(BaseModel):
    listing_id: int
    otp_type: OtpType
    resend: bool = False


class SendOtpResponse(BaseModel):
    message: str
    otp_event_id: int
    listing_id: int
    otp_type: OtpType
    expires_at: datetime


class VerifyOtpRequest(BaseModel):
    listing_id: int | None = None
    otp_type: OtpType
    otp_code: str = Field(min_length=6, max_length=6)

    @field_validator("otp_code")
    @classmethod
    def otp_code_must_be_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("otp_code must contain only digits")
        return value


class VerifyOtpResponse(BaseModel):
    message: str
    otp_event_id: int
    otp_type: OtpType
    listing_id: int | None = None
    listing_status: str | None = None
