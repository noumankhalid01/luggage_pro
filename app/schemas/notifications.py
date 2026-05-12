from pydantic import BaseModel


class Notification(BaseModel):
    fcm_token: str
    title: str
    body: str
    data: dict[str, str] = {}