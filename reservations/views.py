from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from rest_framework.views import APIView
from django.utils import timezone
from .permissions import IsShopManager
from django.db import transaction
from rest_framework.permissions import AllowAny
from shops.models import (DiningTable,Shop,ShopStaff,ShopOperatingHours,)
from .models import Reservation, ReservationTable
from .serializers import (ReservationSerializer,ReservationTableSerializer,)
from .availability import get_available_tables
from django.shortcuts import get_object_or_404

class ReservationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Reservation.objects.select_related("shop", "user").filter(user=self.request.user)
        shop_id = self.request.query_params.get("shop_id")
        reservation_date = self.request.query_params.get("reservation_date")

        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)

        if reservation_date:
            queryset = queryset.filter( reservation_date=reservation_date)

        return queryset

    def perform_create(self, serializer):
        from notifications.services import create_notification
        with transaction.atomic():
            reservation = serializer.save(user=self.request.user)
            create_notification(
                reservation=reservation,
                notification_type="BOOKING_RECEIVED",
                message=(
                    f"Your reservation {reservation.booking_code} "
                    "has been received and is pending confirmation."
                ),
            )

class ReservationDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Reservation.objects.select_related("shop","user").filter(user=self.request.user)



class ReservationCancelAPIView(generics.GenericAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        from notifications.services import create_notification

        cancellation_reason = request.data.get("cancellation_reason", "")
        with transaction.atomic():
            reservation = get_object_or_404(self.get_queryset().select_for_update(),
                pk=self.kwargs.get("pk")
            )

            if reservation.status in [
                "CANCELLED",
                "COMPLETED",
                "NO_SHOW",
                "REJECTED",
            ]:
                return Response(
                    {
                        "detail": "This reservation cannot be cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            reservation.status = "CANCELLED"
            reservation.cancellation_reason = cancellation_reason
            reservation.cancelled_at = timezone.now()
            reservation.save(
                update_fields=[
                    "status",
                    "cancellation_reason",
                    "cancelled_at",
                    "last_update"
                ]
            )

            create_notification(reservation=reservation,notification_type="BOOKING_CANCELLED",
                message=(
                    f"Your reservation {reservation.booking_code} "
                    "has been cancelled successfully."
                ),
            )
        serializer = self.get_serializer(reservation)
        return Response(serializer.data,status=status.HTTP_200_OK)


class ReservationApproveAPIView(generics.GenericAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsShopManager]

    def get_queryset(self):
        return Reservation.objects.select_related("shop", "user").all()

    def post(self, request, *args, **kwargs):
        from notifications.services import create_notification

        with transaction.atomic():
            reservation = self.get_queryset().select_for_update().get(pk=kwargs.get("pk"))
            self.check_object_permissions(request, reservation)

            if reservation.status != "PENDING":
                return Response(
                    {"detail": "Only pending reservations can be approved."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            available_tables = get_available_tables(reservation,lock_tables=True)

            if not available_tables:
                return Response(
                    {
                        "detail": (
                            "No suitable dining table is available "
                            "for this reservation."
                        )
                    },
                    status=status.HTTP_409_CONFLICT
                )

            selected_table = available_tables[0]
            reservation.status = "CONFIRMED"
            reservation.confirmed_at = timezone.now()
            reservation.save(update_fields=["status","confirmed_at","last_update"])

            ReservationTable.objects.create(reservation=reservation,dining_table=selected_table)

            create_notification( reservation=reservation,
                notification_type="BOOKING_CONFIRMED",
                message=(
                    f"Your reservation {reservation.booking_code} "
                    "has been confirmed."
                ),
            )

        serializer = self.get_serializer(reservation)
        response_data = serializer.data
        response_data["assigned_table"] = {
            "id": selected_table.id,
            "table_number": selected_table.table_number,
            "capacity": selected_table.capacity,
        }

        return Response(response_data,status=status.HTTP_200_OK)



class ReservationRejectAPIView(generics.GenericAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsShopManager]

    def get_queryset(self):
        return Reservation.objects.select_related("shop", "user").select_for_update()

    def post(self, request, *args, **kwargs):
        from notifications.services import create_notification
        with transaction.atomic():
            reservation = self.get_object()

            if reservation.status != "PENDING":
                return Response(
                    {
                        "detail": "Only pending reservations can be rejected."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            reservation.status = "REJECTED"
            reservation.save(update_fields=["status", "last_update"])

            create_notification(reservation=reservation,notification_type="BOOKING_REJECTED",
                message=(
                    f"Your reservation {reservation.booking_code} "
                    "has been rejected by the restaurant."
                ),
            )

        serializer = self.get_serializer(reservation)

        return Response(serializer.data,status=status.HTTP_200_OK)


class ReservationTableAssignAPIView(generics.GenericAPIView):
    serializer_class = ReservationTableSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        reservation_id = kwargs.get("reservation_id")

        try:
            with transaction.atomic():
                reservation = (Reservation.objects.select_for_update().select_related("shop").get(pk=reservation_id))

                is_manager = ShopStaff.objects.filter(shop=reservation.shop,user=request.user,role="MANAGER",is_active=True).exists()

                if not is_manager:
                    return Response(
                        {
                            "detail": (
                                "Only an active manager of this shop "
                                "can assign dining tables."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                dining_table_id = request.data.get("dining_table")

                if dining_table_id is not None:
                    DiningTable.objects.select_for_update().filter(pk=dining_table_id).first()

                serializer = self.get_serializer(
                    data={
                        "reservation": reservation.id,
                        "dining_table": dining_table_id
                    }
                )
                serializer.is_valid(raise_exception=True)
                assignment = serializer.save()

        except Reservation.DoesNotExist:
            return Response(
                {"detail": "Reservation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(self.get_serializer(assignment).data,status=status.HTTP_201_CREATED)


class ReservationAvailabilityAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        shop_id = request.query_params.get("shop_id")
        reservation_date = request.query_params.get("reservation_date")
        start_time = request.query_params.get("start_time")
        guests = request.query_params.get("guests")
        duration_minutes = request.query_params.get("duration_minutes",90)

        if not all([shop_id,reservation_date,start_time,guests]):
            return Response({
                "detail":(
                    "shop_id, reservation_date, start_time, and guests are required."
                )
            },status=status.HTTP_400_BAD_REQUEST)
        
        try:
            shop_id = int(shop_id)
            guests = int(guests)
            duration_minutes = int(duration_minutes)
            reservation_date = datetime.strptime(reservation_date, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time, "%H:%M").time()

        except(ValueError, TypeError):
            return Response({"detail": "Invalid query parameter format."},
                            status=status.HTTP_400_BAD_REQUEST
                    )

        if shop_id <= 0 or guests <= 0 or duration_minutes <= 0:
            return Response({"detail": 
                            "shop_id, guests, and duration_minutes must be greater than zero."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if reservation_date < timezone.localdate():
            return Response(
                {"detail": "Reservations cannot made for past dates"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            shop = Shop.objects.get(pk= shop_id,is_active=True)

        except Shop.DoesNotExist:
            return Response({
                "detail": "Active restaurants not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        weekday = reservation_date.weekday()
        operating_hours = ShopOperatingHours.objects.filter(shop=shop,weekday=weekday).first()
        if not operating_hours or operating_hours.is_closed:
            return Response({
                "detail": "The restaurant is closed on this day.",
                "available_tables": []
            },
            status=status.HTTP_200_OK
        )

        requested_start = datetime.combine(reservation_date,start_time)
        requested_end = requested_start + timedelta(minutes=duration_minutes)
        opening_datetime = datetime.combine(reservation_date, operating_hours.opening_time)
        closing_datetime = datetime.combine(reservation_date, operating_hours.closing_time)

        if(requested_start < opening_datetime or requested_end > closing_datetime):
            return Response(
                {
                    "detail": (
                        "The requested reservation time is outside "
                        "the restaurant's operating hours."
                    ),
                    "available_tables": []
                },
                status=status.HTTP_200_OK
            )
        requested_start = timezone.make_aware(requested_start)
        requested_end = timezone.make_aware(requested_end)

        if requested_start <= timezone.now():
            return Response(
                {"detail": "The reservation start time must be in the future."},
                status=status.HTTP_400_BAD_REQUEST
            )

        available_tables = DiningTable.objects.filter(shop=shop,is_active=True,capacity__gte=guests).order_by("capacity", "table_number")

        assignments = ReservationTable.objects.filter(
            dining_table__in=available_tables,
            reservation__status="CONFIRMED"
        ).select_related("reservation", "dining_table")

        occupied_table_ids = set()

        for assignment in assignments:
            existing_reservation = assignment.reservation
            existing_start = datetime.combine(existing_reservation.reservation_date,existing_reservation.start_time)
            existing_end = existing_start + timedelta(minutes=existing_reservation.duration_minutes)
            existing_start = timezone.make_aware(existing_start)
            existing_end = timezone.make_aware(existing_end)

            if(requested_start < existing_end and requested_end > existing_start):
                occupied_table_ids.add(assignment.dining_table_id)

            available_tables = available_tables.exclude(id__in=occupied_table_ids)
        table_data = [
            {
                "id": table.id,
                "table_number": table.table_number,
                "capacity": table.capacity
            }
            for table in available_tables
        ]
        return Response(
            {
                "shop_id": shop.id,
                "reservation_date": reservation_date,
                "start_time": start_time,
                "guests": guests,
                "duration_minutes": duration_minutes,
                "available_tables": table_data
            },
            status=status.HTTP_200_OK
        )
