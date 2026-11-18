from django.urls import path
from .views import (
    ReservationListCreateAPIView,
    ReservationDetailAPIView,
    ReservationCancelAPIView,
    ReservationApproveAPIView,
    ReservationRejectAPIView,
    ReservationTableAssignAPIView,
    ReservationAvailabilityAPIView, 
    ) 
urlpatterns =[
    path("",ReservationListCreateAPIView.as_view(),name = "reservation-list-create"),
    path("<int:pk>/",ReservationDetailAPIView.as_view(),name="reservation-detail"),
    path("<int:pk>/cancel/",ReservationCancelAPIView.as_view(),name="reservation-cancel"),
    path("<int:pk>/approve/",ReservationApproveAPIView.as_view(),name="reservation-approve"),
    path("<int:pk>/reject/",ReservationRejectAPIView.as_view(),name="reservation-reject"),
    path("<int:reservation_id>/assign-table/",ReservationTableAssignAPIView.as_view(),name="reservation-assign-table"),
    path("availability/",ReservationAvailabilityAPIView.as_view(),name="reservation-availability")
]