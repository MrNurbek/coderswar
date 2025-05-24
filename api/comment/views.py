from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.comment.models import Comment
from .serializers import CommentSerializer


class CommentPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class CommentCreateAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Komment yozish",
        operation_description="Foydalanuvchi sayt haqida izoh (komment) yozadi. Avtorizatsiya talab qilinadi.",
        request_body=CommentSerializer,
        responses={201: CommentSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentListAPIView(generics.ListAPIView):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CommentPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Nechinchi sahifa (paginatsiya)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Bir sahifada nechta natija ko‘rsatilsin (max: 20)",
                type=openapi.TYPE_INTEGER
            ),
        ],
        operation_summary="Kommentlar ro'yxati",
        operation_description="Barcha foydalanuvchilar yozgan kommentlar ro‘yxatini paginatsiya bilan qaytaradi.",
        responses={200: CommentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
