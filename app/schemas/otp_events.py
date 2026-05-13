from datetime import datetime
from pydantic import BaseModel

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
