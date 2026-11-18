
from django.conf import settings
from django.db import models
from django.db.models import Q


class Reservation(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
        ("NO_SHOW", "No Show"),
    ]

    id = models.BigAutoField(primary_key=True)
    booking_code = models.CharField(max_length=20,unique=True)
    shop = models.ForeignKey("shops.Shop",
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    reservation_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField(default=90)
    guests = models.IntegerField()
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=15)
    special_request = models.TextField(null=True,blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    cancellation_reason = models.TextField(null=True,blank=True)
    confirmed_at = models.DateTimeField(null=True,blank=True)
    cancelled_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(guests__gt=0),
                name="reservation_guests_gt_zero"
            ),
            models.CheckConstraint(
                condition=Q(duration_minutes__gt=0),
                name="reservation_duration_gt_zero"
            ),
        ]

    def __str__(self):
        return f"{self.booking_code} - {self.customer_name}"



class ReservationTable(models.Model):
    id = models.BigAutoField(primary_key=True)

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="table_assignments"
    )

    dining_table = models.ForeignKey(
        "shops.DiningTable",
        on_delete=models.CASCADE,
        related_name="reservation_assignments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["reservation"],
                name="unique_reservation_table_assignment"
            )
        ]

    def __str__(self):
        return (
            f"{self.reservation.booking_code} - "
            f"{self.dining_table.table_number}"
        )
