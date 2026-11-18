
from django.utils import timezone

from .models import Notification

def create_notification(
    reservation,
    notification_type,
    message,
    delivery_channel="IN_APP",
):
    """
    Create an in-app notification for a reservation event.
    """

    notification = Notification.objects.create(
        reservation=reservation,
        notification_type=notification_type,
        delivery_channel=delivery_channel,
        delivery_status="SENT",
        message=message,
        sent_at=timezone.now(),
    )

    return notification
