
from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import IntegrityError, transaction
from shops.models import Shop, DiningTable
from reservations.models import Reservation, ReservationTable
from reservations.availability import get_available_tables


User = get_user_model()


class ReservationAvailabilityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="availability_customer",
            password="testpassword123"
        )

        self.shop = Shop.objects.create(
            shop_name="Test Restaurant",
            address="Test Address",
            city="Coimbatore",
            is_active=True
        )

        self.table1 = DiningTable.objects.create(
            shop=self.shop,
            table_number="T01",
            capacity=4,
            is_active=True
        )

        self.table2 = DiningTable.objects.create(
            shop=self.shop,
            table_number="T02",
            capacity=6,
            is_active=True
        )

        self.table3 = DiningTable.objects.create(
            shop=self.shop,
            table_number="T03",
            capacity=2,
            is_active=False
        )

        self.reservation = self.create_reservation(
            booking_code="TEST-AVAIL-001",
            guests=4,
            start_time=time(19, 0)
        )

    def create_reservation(
        self,
        booking_code,
        guests=4,
        start_time=time(19, 0),
        status="PENDING",
        duration_minutes=90
    ):
        return Reservation.objects.create(
            booking_code=booking_code,
            shop=self.shop,
            user=self.user,
            reservation_date=date(2026, 12, 1),
            start_time=start_time,
            duration_minutes=duration_minutes,
            guests=guests,
            customer_name="Test Customer",
            customer_phone="9876543210",
            status=status
        )

    def test_only_active_tables_with_sufficient_capacity_are_returned(self):
        available_tables = get_available_tables(self.reservation)

        self.assertEqual(
            [table.table_number for table in available_tables],
            ["T01", "T02"]
        )

    def test_tables_are_ordered_by_smallest_capacity_first(self):
        reservation = self.create_reservation(
            booking_code="TEST-AVAIL-002",
            guests=2
        )

        available_tables = get_available_tables(reservation)

        self.assertEqual(
            [table.table_number for table in available_tables],
            ["T01", "T02"]
        )

    def test_overlapping_confirmed_reservation_blocks_assigned_table(self):
        existing_reservation = self.create_reservation(
            booking_code="TEST-AVAIL-003",
            guests=4,
            start_time=time(19, 0),
            status="CONFIRMED"
        )

        ReservationTable.objects.create(
            reservation=existing_reservation,
            dining_table=self.table1
        )

        available_tables = get_available_tables(self.reservation)

        self.assertEqual(
            [table.table_number for table in available_tables],
            ["T02"]
        )

    def test_non_overlapping_reservation_does_not_block_table(self):
        existing_reservation = self.create_reservation(
            booking_code="TEST-AVAIL-004",
            guests=4,
            start_time=time(17, 0),
            status="CONFIRMED"
        )

        ReservationTable.objects.create(
            reservation=existing_reservation,
            dining_table=self.table1
        )

        available_tables = get_available_tables(self.reservation)

        self.assertEqual(
            [table.table_number for table in available_tables],
            ["T01", "T02"]
        )
class ReservationModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="model_customer",
            password="testpassword123"
        )

        self.shop = Shop.objects.create(
            shop_name="Model Test Restaurant",
            address="Test Address",
            city="Coimbatore"
        )

    def create_reservation(self, booking_code):
        return Reservation.objects.create(
            booking_code=booking_code,
            shop=self.shop,
            user=self.user,
            reservation_date=date(2026, 12, 1),
            start_time=time(19, 0),
            duration_minutes=90,
            guests=4,
            customer_name="Model Test Customer",
            customer_phone="9876543210"
        )

    def test_duplicate_booking_code_is_rejected(self):
        self.create_reservation("MODEL-TEST-001")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_reservation("MODEL-TEST-001")

    def test_only_one_table_can_be_assigned_to_reservation(self):
        reservation = self.create_reservation("MODEL-TEST-002")

        table1 = DiningTable.objects.create(
            shop=self.shop,
            table_number="M01",
            capacity=4
        )

        table2 = DiningTable.objects.create(
            shop=self.shop,
            table_number="M02",
            capacity=6
        )

        ReservationTable.objects.create(
            reservation=reservation,
            dining_table=table1
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ReservationTable.objects.create(
                    reservation=reservation,
                    dining_table=table2
                )
