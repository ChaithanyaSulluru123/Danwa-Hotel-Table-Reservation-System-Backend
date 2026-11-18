
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Shop, DiningTable,ShopOperatingHours,ShopStaff
from .serializers import ShopSerializer, DiningTableSerializer,ShopOperatingHoursSerializer,ShopStaffSerializer
from rest_framework.response import Response
from rest_framework import status
from .serializers import ShopSerializer

class ShopListCreateAPIView(generics.ListCreateAPIView):
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class ShopDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class ShopDeactivateAPIView(generics.GenericAPIView):
    queryset = Shop.objects.filter(is_active=True)
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        shop = self.get_object()
        shop.is_active = False
        shop.save(update_fields=["is_active", "last_update"])
        serializer = ShopSerializer(shop)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class DiningTableListAPIView(generics.ListCreateAPIView):
    queryset = DiningTable.objects.filter(is_active = True)
    serializer_class = DiningTableSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        queryset = DiningTable.objects.filter(is_active = True)
        shop_id = self.request.query_params.get("shop_id")
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        return queryset
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


class DiningTableDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = DiningTable.objects.select_related("shop").all()
    serializer_class = DiningTableSerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

class DiningTableDeactivateAPIView(generics.GenericAPIView):
    queryset = DiningTable.objects.filter(is_active=True)
    serializer_class = DiningTableSerializer
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        dining_table = self.get_object()
        dining_table.is_active = False
        dining_table.save(update_fields=["is_active"])
        serializer = self.get_serializer(dining_table)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class ShopOperatingHoursListCreateAPIView(generics.ListCreateAPIView):
    queryset = ShopOperatingHours.objects.select_related("shop").all()
    serializer_class = ShopOperatingHoursSerializer
    def get_queryset(self):
        queryset = ShopOperatingHours.objects.select_related("shop").all()
        shop_id = self.request.query_params.get("shop_id")
        weekday = self.request.query_params.get("weekday")
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        if weekday is not None:
            queryset = queryset.filter(weekday=weekday)
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class ShopOperatingHoursDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ShopOperatingHours.objects.select_related("shop").all()
    serializer_class = ShopOperatingHoursSerializer
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class ShopStaffListCreateAPIView(generics.ListCreateAPIView):
    queryset= ShopStaff.objects.select_related("shop","user").all()
    serializer_class = ShopStaffSerializer
    permission_classes= [IsAdminUser]
    def get_queryset(self):
        queryset = ShopStaff.objects.select_related("shop", "user").all()
        shop_id = self.request.query_params.get("shop_id")
        is_active = self.request.query_params.get("is_active")
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        if is_active is not None:
            if is_active.lower() in ["true", "1"]:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ["false", "0"]:
                queryset = queryset.filter(is_active=False)
        return queryset

class ShopStaffDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ShopStaff.objects.select_related("shop", "user").all()
    serializer_class = ShopStaffSerializer
    permission_classes = [IsAdminUser]

class ShopStaffDeactivateAPIView(generics.GenericAPIView):
    queryset = ShopStaff.objects.all()
    serializer_class = ShopStaffSerializer
    permission_classes = [IsAdminUser]
    def post(self, request, *args, **kwargs):
        staff = self.get_object()
        if not staff.is_active:
            return Response(
                {"detail": "This staff assignment is already inactive."},
                status=status.HTTP_400_BAD_REQUEST
            )
        staff.is_active = False
        staff.save(update_fields=["is_active"])
        serializer = self.get_serializer(staff)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )