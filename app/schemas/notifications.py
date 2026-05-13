from pydantic import BaseModel, Field


class Notification(BaseModel):
    fcm_token: str
    title: str
    body: str
    data: dict[str, str] = Field(default_factory=dict)
