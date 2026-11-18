from django.urls import path

from .views import (
    ShopListCreateAPIView,
    ShopDetailAPIView,
    ShopDeactivateAPIView,
    DiningTableListAPIView,
    DiningTableDetailAPIView,
    DiningTableDeactivateAPIView,
    ShopOperatingHoursListCreateAPIView,
    ShopOperatingHoursDetailAPIView,
    ShopStaffListCreateAPIView,
    ShopStaffDetailAPIView,
    ShopStaffDeactivateAPIView,
)

urlpatterns = [
    path( "",ShopListCreateAPIView.as_view(),name="shop-list-create"),
    path("<int:pk>/",ShopDetailAPIView.as_view(),name="shop-detail"),
    path("<int:pk>/deactivate/",ShopDeactivateAPIView.as_view(),name="shop-deactivate"),
    path("tables/",DiningTableListAPIView.as_view(),name="dining-tables-list"),
    path("tables/<int:pk>/",DiningTableDetailAPIView.as_view(),name="dining-table-detail"),
    path("tables/<int:pk>/deactivate/",DiningTableDeactivateAPIView.as_view(),name="dining-table-deactivate"),
    path("operating-hours/",ShopOperatingHoursListCreateAPIView.as_view(),name="shop-operating-hours-list"),
    path("operating-hours/<int:pk>/", ShopOperatingHoursDetailAPIView.as_view(),name="shop-operating-hours-detail"),
    path("staff/",ShopStaffListCreateAPIView.as_view(),name="shop-staff-list-create"),
    path("staff/<int:pk>/",ShopStaffDetailAPIView.as_view(),name="shop-staff-detail"),
    path("staff/<int:pk>/deactivate/",ShopStaffDeactivateAPIView.as_view(),name="shop-staff-deactivate"),
]