from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.mainquest.models import Topic, UserProgress
from .serializers import TopicSerializer, TopicShortSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone


class TopicListAPIView(generics.ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicShortSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="C# bo‘yicha barcha mavzular va har bir mavzudagi rejalar ro‘yxatini qaytaradi. Faqat id va title qaytariladi.",
        responses={200: TopicShortSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)





class TopicDetailAPIView(RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        topic = super().get_object()
        user = self.request.user
        previous_topics = Topic.objects.filter(order__lt=topic.order).order_by('order')

        for prev in previous_topics:
            if not UserProgress.objects.filter(user=user, topic=prev, is_completed=True).exists():
                raise PermissionDenied(f"You must complete previous topic: {prev.title}")
        return topic



class MarkTopicCompletedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        progress, created = UserProgress.objects.get_or_create(user=request.user, topic=topic)
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return Response({"message": "Topic marked as completed"})
