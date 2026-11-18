
from django.conf import settings
from django.db import models
from django.db.models import Q

class Shop(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop_name = models.CharField(max_length=150)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        #db_table = "shops"
        ordering = ["shop_name"]
    def __str__(self):
        return self.shop_name


class DiningTable(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="dining_tables"
    )
    table_number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["shop", "table_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "table_number"],
                name="unique_table_number_per_shop"
            )
        ]
    def __str__(self):
        return f"{self.shop.shop_name} - {self.table_number}"


class ShopOperatingHours(models.Model):
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="operating_hours"
    )
    weekday = models.IntegerField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    class Meta:
        ordering = ["shop", "weekday"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "weekday"],
                name="unique_shop_weekday"
            )
        ]
    def __str__(self):
        return f"{self.shop.shop_name} - Weekday {self.weekday}"


class ShopStaff(models.Model):
    ROLE_CHOICES = [
        ("MANAGER", "Manager"),
        ("STAFF", "Staff"),
    ]
    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="staff_members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shop_staff_assignments"
    )
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["shop", "user"]
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "user"],
                condition=Q(is_active=True),
                name="unique_active_staff_per_shop"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.shop.shop_name} ({self.role})"
