from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.mainquest.models import Topic, UserProgress
from apps.userapp.models import User
from .serializers import TopicSerializer, TopicShortSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

COMPLETION_POINTS = 22

class MarkTopicCompletedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)

        # Bir xil user-topic progress qatorini qulflash bilan olamiz (concurrency xavfsiz)
        progress, created = (
            UserProgress.objects.select_for_update()
            .get_or_create(
                user=request.user,
                topic=topic,
                defaults={
                    "is_completed": True,
                    "completed_at": timezone.now(),
                    "score": COMPLETION_POINTS,
                },
            )
        )

        added_points = 0

        if created:
            # Yangi yozuv: 22 ball qo‘shiladi
            User.objects.filter(pk=request.user.pk).update(
                rating=F("rating") + COMPLETION_POINTS
            )
            added_points = COMPLETION_POINTS
        else:
            # Mavjud yozuv bo‘lsa:
            # Agar allaqachon yakunlangan va 22 berilgan bo‘lsa — ball qo‘shilmaydi
            if progress.is_completed and (progress.score or 0) >= COMPLETION_POINTS:
                request.user.refresh_from_db(fields=["rating"])
                return Response(
                    {
                        "message": "Mavzu allaqachon yakunlangan. Reytingga qayta ball qo‘shilmaydi.",
                        "topic_id": topic.pk,
                        "rating": request.user.rating,
                        "added_points": 0,
                    },
                    status=status.HTTP_200_OK,
                )

            # Agar eski ma'lumotda is_completed=False yoki score<22 bo‘lsa — to‘ldirib yuboramiz
            prev_score = progress.score or 0
            progress.is_completed = True
            if not progress.completed_at:
                progress.completed_at = timezone.now()
            # Faqat yetishmayotgan qismi qo‘shiladi (odatda 22 - prev_score)
            added_points = max(0, COMPLETION_POINTS - prev_score)
            progress.score = max(progress.score or 0, COMPLETION_POINTS)
            progress.save(update_fields=["is_completed", "completed_at", "score"])

            if added_points > 0:
                User.objects.filter(pk=request.user.pk).update(
                    rating=F("rating") + added_points
                )

        # Yangilangan ratingni qayta o‘qiymiz
        request.user.refresh_from_db(fields=["rating"])

        return Response(
            {
                "message": "Mavzu yakunlandi",
                "topic_id": topic.pk,
                "added_points": added_points,
                "rating": request.user.rating,
            },
            status=status.HTTP_200_OK,
        )


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



# class MarkTopicCompletedAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, pk):
#         topic = get_object_or_404(Topic, pk=pk)
#         progress, created = UserProgress.objects.get_or_create(user=request.user, topic=topic)
#         progress.is_completed = True
#         progress.completed_at = timezone.now()
#         progress.save()
#         return Response({"message": "Topic marked as completed"})
