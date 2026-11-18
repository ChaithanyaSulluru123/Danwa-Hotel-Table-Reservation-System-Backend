from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Notification.objects.filter(reservation__user=self.request.user).select_related("reservation","reservation__shop")
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            if is_read.lower() in ["true", "1"]:
                queryset = queryset.filter(is_read=True)

            elif is_read.lower() in ["false", "0"]:
                queryset = queryset.filter(is_read=False)

        return queryset


class NotificationDetailAPIView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Notification.objects.filter(reservation__user=self.request.user).select_related("reservation","reservation__shop")


class NotificationMarkReadAPIView(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Notification.objects.filter(reservation__user=self.request.user)

    def post(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.is_read:
            return Response(
                {
                    "detail": "This notification is already marked as read."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
        serializer = self.get_serializer(notification)
        return Response(serializer.data,status=status.HTTP_200_OK)