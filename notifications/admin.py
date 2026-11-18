from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "reservation",
        "notification_type",
        "delivery_channel",
        "delivery_status",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "notification_type",
        "delivery_channel",
        "delivery_status",
        "is_read",
    ]

    search_fields = [
        "message",
        "reservation__booking_code",
        "reservation__customer_name",
    ]

    readonly_fields = [
        "created_at",
        "sent_at",
        "read_at",
    ]

    ordering = ["-created_at"]