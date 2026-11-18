from django.urls import path

from .views import (
    NotificationListAPIView,
    NotificationDetailAPIView,
    NotificationMarkReadAPIView,
)

urlpatterns = [

    path("",NotificationListAPIView.as_view(),name="notification-list"),
    path("<int:pk>/",NotificationDetailAPIView.as_view(),name="notification-detail"),
    path("<int:pk>/mark-read/",NotificationMarkReadAPIView.as_view(),name="notification-mark-read"),

]