from django.contrib import admin
from .models import Shop, DiningTable, ShopOperatingHours

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display= (
        "id",
        "shop_name",
        "address",
        "city",
        "phone",
        "is_active",
        "created_at",
        "last_update",

    )
    list_filter = ("is_active","city")
    search_fields =(
        "shop_name",
        "address",
        "city",
        "phone",
    )
@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shop",
        "table_number",
        "capacity",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "shop")
    search_fields = ("table_number", "shop__shop_name")

@admin.register(ShopOperatingHours)
class ShopOperatingHoursAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shop",
        "weekday",
        "opening_time",
        "closing_time",
        "is_closed",
    )
    list_filter = ("shop","weekday","is_closed")
    search_fields =("shop__shop_name",)