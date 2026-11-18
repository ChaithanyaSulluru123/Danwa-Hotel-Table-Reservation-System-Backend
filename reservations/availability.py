
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from shops.models import DiningTable
from .models import ReservationTable


def get_available_tables(reservation, lock_tables=False):
    """
    Return active tables that can accommodate the reservation.

    Tables are ordered by smallest capacity first.
    Overlapping confirmed reservations are excluded.
    """

    candidate_queryset = DiningTable.objects.filter(
        shop=reservation.shop,
        is_active=True,
        capacity__gte=reservation.guests
    ).order_by("capacity", "table_number")

    if lock_tables:
        candidate_queryset = candidate_queryset.select_for_update()

    candidate_tables = list(candidate_queryset)

    if not candidate_tables:
        return []

    requested_start = datetime.combine(
        reservation.reservation_date,
        reservation.start_time
    )

    requested_end = requested_start + timedelta(
        minutes=reservation.duration_minutes
    )

    requested_start = timezone.make_aware(requested_start)
    requested_end = timezone.make_aware(requested_end)

    assignments = ReservationTable.objects.filter(
        dining_table__in=candidate_tables,
        reservation__status="CONFIRMED"
    ).exclude(
        reservation=reservation
    ).select_related("reservation")

    occupied_table_ids = set()

    for assignment in assignments:
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
            occupied_table_ids.add(assignment.dining_table_id)

    available_tables = [
        table
        for table in candidate_tables
        if table.id not in occupied_table_ids
    ]

    return available_tables
