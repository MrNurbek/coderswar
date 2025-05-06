from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.content.models import Content
from .serializers import ContentSerializer

class ContentListAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'content_type',
                openapi.IN_QUERY,
                description="`home` yoki `personal` qiymatini kiriting",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={200: ContentSerializer(many=True)},
        operation_summary="Barcha kontentlarni olish",
        operation_description="Ushbu API orqali `Content` modelidagi barcha kontentlar ro'yxati olinadi. "
                              "Agar `content_type` query parametri berilsa, shunga mos kontentlar qaytariladi.",
    )
    def get(self, request):
        content_type = request.query_params.get('content_type', None)
        queryset = Content.objects.all()
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        serializer = ContentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
