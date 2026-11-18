from rest_framework import serializers
from .models import Shop,DiningTable,ShopOperatingHours,ShopStaff

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            "id",
            "shop_name",
            "address",
            "city",
            "phone",
            "is_active",
            "created_at",
            "last_update",
        ]
        
        read_only_fields = [
            "id",
            "created_at",
            "last_update",
        ]

class DiningTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiningTable
        fields = [
            "id",
            "shop",
            "table_number",
            "capacity",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Table capacity must be greater than zero.")

        return value

    def validate_shop(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot add a table to an inactive shop."
            )
        return value

class ShopOperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopOperatingHours
        fields = [
            "id",
            "shop",
            "weekday",
            "opening_time",
            "closing_time",
            "is_closed",
        ]
        read_only_fields = ["id"]

    def validate_shop(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot configure operating hours for an inactive shop."
            )
        return value

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        opening_time = attrs.get(
            "opening_time",
            instance.opening_time if instance else None
        )

        closing_time = attrs.get(
            "closing_time",
            instance.closing_time if instance else None
        )

        is_closed = attrs.get(
            "is_closed",
            instance.is_closed if instance else False
        )

        if is_closed:
            return attrs

        if not opening_time or not closing_time:
            raise serializers.ValidationError(
                "Opening time and closing time are required when the shop is open."
            )

        if opening_time >= closing_time:
            raise serializers.ValidationError(
                "Opening time must be earlier than closing time."
            )

        return attrs

class ShopStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopStaff
        fields =[
             "id",
            "shop",
            "user",
            "role",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
    def validate_shop(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign staff to an inactive shop."
            )
        return value