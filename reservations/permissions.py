from rest_framework.permissions import BasePermission
from shops.models import ShopStaff
class IsShopManager(BasePermission):
    message = "Only an active manager of this shop can perform this action."
    def has_object_permission(self, request, view, obj):
        return ShopStaff.objects.filter(
            shop=obj.shop,
            user=request.user,
            role="MANAGER",
            is_active=True
        ).exists()