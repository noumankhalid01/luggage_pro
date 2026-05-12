from firebase_admin import messaging

from app.schemas.notifications import Notification

def send_push_notification(notification: Notification) -> bool:
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
            ),
            data={str(k): str(v) for k, v in notification.data.items()}, 
            token=notification.fcm_token,
        )
        messaging.send(message)
        return True
    except Exception as e:
        print(f"FCM error: {e}")
        return False