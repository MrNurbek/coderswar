from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.content.models import Content
from .serializers import ContentSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .filters import ContentFilter

class ContentListAPIView(generics.ListAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContentFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'content_type',
                openapi.IN_QUERY,
                description="`home` yoki `personal` qiymatini kiriting",
                type=openapi.TYPE_STRING
            ),
        ],
        operation_summary="Content ro'yxati",
        operation_description="content_type bo‘yicha filterlash imkoniyati mavjud.",
        responses={200: ContentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

