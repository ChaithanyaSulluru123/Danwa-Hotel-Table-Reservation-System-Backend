from django.contrib import admin
from .models import Reservation, ReservationTable
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking_code",
        "shop",
        "user",
        "reservation_date",
        "start_time",
        "guests",
        "status",
    )
    list_filter = (
        "status",
        "reservation_date",
        "shop",
    )
    search_fields = (
        "booking_code",
        "customer_name",
        "customer_phone",
        "user__username",
    )
@admin.register(ReservationTable)
class ReservationTableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reservation",
        "dining_table",
        "created_at",
    )
    search_fields = (
        "reservation__booking_code",
        "dining_table__table_number",
    )
