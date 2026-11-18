from uuid import uuid4
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import serializers
from shops.models import DiningTable, ShopOperatingHours
from .models import Reservation, ReservationTable
import re


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            "id",
            "booking_code",
            "shop",
            "user",
            "reservation_date",
            "start_time",
            "duration_minutes",
            "guests",
            "customer_name",
            "customer_phone",
            "special_request",
            "status",
            "cancellation_reason",
            "confirmed_at",
            "cancelled_at",
            "created_at",
            "last_update",
        ]
        read_only_fields = [
            "id",
            "booking_code",
            "user",
            "status",
            "cancellation_reason",
            "confirmed_at",
            "cancelled_at",
            "created_at",
            "last_update",
        ]

    def validate_shop(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot create a reservation for an inactive shop."
            )

        return value

    def validate_customer_phone(self, value):
        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise serializers.ValidationError(
            "Enter a valid 10-digit Indian mobile number."
        )

        return value

    def validate(self, attrs):
        shop = attrs.get("shop",self.instance.shop if self.instance else None)
        reservation_date = attrs.get("reservation_date",self.instance.reservation_date if self.instance else None)
        start_time = attrs.get("start_time",self.instance.start_time if self.instance else None)
        guests = attrs.get("guests",self.instance.guests if self.instance else None)
        duration_minutes = attrs.get("duration_minutes",self.instance.duration_minutes if self.instance else 90)

        if any(value is None for value in[
            shop,
            reservation_date,
            start_time,
            guests,
            duration_minutes
        ]):
            return attrs
          
        if guests <= 0:
            raise serializers.ValidationError({
                "guests": "Guest count must be greater than zero."
            })

        if duration_minutes <= 0:
            raise serializers.ValidationError({
                "duration_minutes": "Reservation duration must be greater than zero."
            })

        requested_start = datetime.combine(reservation_date,start_time)
        current_time = timezone.localtime().replace(tzinfo=None)

        if requested_start <= current_time:
            raise serializers.ValidationError({
                "reservation_date": "Reservations cannot be created for a past date or time."
            })

        weekday = reservation_date.weekday()
        operating_hours = ShopOperatingHours.objects.filter(shop=shop,weekday=weekday).first()

        if not operating_hours or operating_hours.is_closed:
            raise serializers.ValidationError({
                "reservation_date": "The restaurant is closed on this day."
            })

        requested_end = requested_start + timedelta(minutes=duration_minutes)
        opening_datetime = datetime.combine(reservation_date,operating_hours.opening_time)

        closing_datetime = datetime.combine(
            reservation_date,
            operating_hours.closing_time
        )
      
        if (requested_start < opening_datetime or requested_end > closing_datetime):
            raise serializers.ValidationError({
                "start_time": "The requested reservation time is outside the restaurant's operating hours."
            })

        candidate_tables = DiningTable.objects.filter(
            shop=shop,
            is_active=True,
            capacity__gte=guests
        )

        if not candidate_tables.exists():
            raise serializers.ValidationError({
                "guests": "No active dining table has enough capacity for this guest count."
            })

        assignments = ReservationTable.objects.filter(
            dining_table__in=candidate_tables,
            reservation__status="CONFIRMED"
        ).select_related("reservation")

        if self.instance:
            assignments = assignments.exclude(
                reservation=self.instance
            )

        occupied_table_ids = set()

        for assignment in assignments:
            existing_reservation = assignment.reservation
            existing_start = datetime.combine(existing_reservation.reservation_date,existing_reservation.start_time)
            existing_end = existing_start + timedelta(minutes=existing_reservation.duration_minutes)
          
            if (requested_start < existing_end and requested_end > existing_start):
                occupied_table_ids.add(assignment.dining_table_id)

        available_tables = candidate_tables.exclude(
            id__in=occupied_table_ids
        )

        if not available_tables.exists():
            raise serializers.ValidationError({
                "reservation_date": "No suitable dining table is available for the selected date and time."
            })

        return attrs

    def create(self, validated_data):
        validated_data["booking_code"] = (
        f"RES-{uuid4().hex[:12].upper()}"
    )

        return Reservation.objects.create(**validated_data)


class ReservationTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationTable
        fields = [
            "id",
            "reservation",
            "dining_table",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
        validators = []

    def validate(self, attrs):
        reservation = attrs["reservation"]
        dining_table = attrs["dining_table"]

        if reservation.status != "CONFIRMED":
            raise serializers.ValidationError({
                "reservation": (
                    "Tables can only be assigned to confirmed reservations."
                )
            })

        existing_reservation_assignment = ReservationTable.objects.filter(
            reservation=reservation
        )

        if self.instance:
            existing_reservation_assignment = (
                existing_reservation_assignment.exclude(
                    pk=self.instance.pk
                )
            )

        if existing_reservation_assignment.exists():
            raise serializers.ValidationError({
                "reservation": (
                    "This reservation already has a dining table assigned."
                )
            })

        if not dining_table.is_active:
            raise serializers.ValidationError({
                "dining_table": "Cannot assign an inactive dining table."
            })

        if dining_table.shop_id != reservation.shop_id:
            raise serializers.ValidationError({
                "dining_table": (
                    "This table does not belong to the reservation's shop."
                )
            })

        if dining_table.capacity < reservation.guests:
            raise serializers.ValidationError({
                "dining_table": (
                    f"This table accommodates only {dining_table.capacity} guests. "
                    f"The reservation requires {reservation.guests} seats."
                )
            })

        duplicate = ReservationTable.objects.filter(
            reservation=reservation,
            dining_table=dining_table
        )

        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise serializers.ValidationError({
                "dining_table": (
                    "This table is already assigned to this reservation."
                )
            })

        requested_start = datetime.combine(
            reservation.reservation_date,
            reservation.start_time
        )

        requested_end = requested_start + timedelta(
            minutes=reservation.duration_minutes
        )

        requested_start = timezone.make_aware(requested_start)
        requested_end = timezone.make_aware(requested_end)

        existing_assignments = ReservationTable.objects.filter(
            dining_table=dining_table,
            reservation__status="CONFIRMED"
        ).select_related("reservation")

        if self.instance:
            existing_assignments = existing_assignments.exclude(
                pk=self.instance.pk
            )

        for assignment in existing_assignments:
            existing_reservation = assignment.reservation

            existing_start = datetime.combine(
                existing_reservation.reservation_date,
                existing_reservation.start_time
            )

            existing_end = existing_start + timedelta(
                minutes=existing_reservation.duration_minutes
            )

            existing_start = timezone.make_aware(existing_start)
            existing_end = timezone.make_aware(existing_end)

            if (
                requested_start < existing_end
                and requested_end > existing_start
            ):
                raise serializers.ValidationError({
                    "dining_table": (
                        f"This table is already assigned to reservation "
                        f"{existing_reservation.booking_code} during this time."
                    )
                })

        return attrs
