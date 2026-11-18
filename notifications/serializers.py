from rest_framework import serializers
from .models import Notification
class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification

        fields = [
            "id",
            "reservation",
            "notification_type",
            "delivery_channel",
            "delivery_status",
            "message",
            "is_read",
            "read_at",
            "created_at",
            "sent_at",
        ]

        read_only_fields = [
            "id",
            "delivery_status",
            "is_read",
            "read_at",
            "created_at",
            "sent_at",
        ]