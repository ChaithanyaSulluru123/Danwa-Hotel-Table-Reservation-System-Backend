from django.db import models
class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ("BOOKING_RECEIVED", "Booking Received"),
        ("BOOKING_CONFIRMED", "Booking Confirmed"),
        ("BOOKING_REJECTED", "Booking Rejected"),
        ("BOOKING_CANCELLED", "Booking Cancelled"),
        ("BOOKING_MODIFIED", "Booking Modified"),
        ("BOOKING_REMINDER", "Booking Reminder"),
    ]

    DELIVERY_CHANNEL_CHOICES = [
        ("IN_APP", "In App"),
        ("SMS", "SMS"),
        ("EMAIL", "Email"),
        ("PUSH", "Push"),
    ]

    DELIVERY_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    id = models.BigAutoField(primary_key=True)

    reservation = models.ForeignKey(
        "reservations.Reservation",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )

    delivery_channel = models.CharField(
        max_length=10,
        choices=DELIVERY_CHANNEL_CHOICES
    )

    delivery_status = models.CharField(
        max_length=10,
        choices=DELIVERY_STATUS_CHOICES,
        default="PENDING"
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.notification_type} - "
            f"Reservation {self.reservation_id}"
        )