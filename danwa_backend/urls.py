from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/shops/", include("shops.urls")),
    path("api/reservations/",include("reservations.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("accounts/profile/",lambda request: redirect("/api/reservations/")),
]
