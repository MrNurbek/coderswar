from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import random
from django.utils import timezone

from api.duels.serializers import DuelSerializer, DuelJoinSerializer, DuelCreateSerializer
from apps.duels.models import Duel, DuelAssignment
from apps.mainquest.models import Assignment
from apps.userapp.models import User
class CreateDuelView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DuelCreateSerializer,
        responses={201: DuelSerializer()},
        operation_description="Foydalanuvchi duel yaratadi, unga 3 ta random topshiriq biriktiriladi."
    )
    def post(self, request):
        user = request.user
        duel = Duel.objects.create(creator=user)
        assignments = Assignment.objects.order_by('?')[:3]
        for a in assignments:
            DuelAssignment.objects.create(duel=duel, assignment=a)
        return Response(DuelSerializer(duel).data, status=status.HTTP_201_CREATED)


class JoinDuelView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DuelJoinSerializer,
        responses={200: 'Duelga qo`shildingiz'},
        operation_description="Boshqa foydalanuvchi mavjud duelga qo`shiladi."
    )
    def post(self, request, duel_id):
        user = request.user
        duel = Duel.objects.filter(id=duel_id, opponent__isnull=True).first()
        if not duel or duel.creator == user:
            return Response({"error": "Duel mavjud emas yoki o'zingizga qo'shila olmaysiz."}, status=400)

        duel.opponent = user
        duel.started_at = timezone.now()
        duel.save()
        return Response({"message": "Duelga qo`shildingiz"}, status=200)


class DuelListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: DuelSerializer(many=True)},
        operation_description="Yaratilgan, lekin hali hech kim qo'shilmagan duellar ro'yxatini qaytaradi."
    )
    def get(self, request):
        duels = Duel.objects.filter(opponent__isnull=True, is_active=True).exclude(creator=request.user)
        return Response(DuelSerializer(duels, many=True).data)
