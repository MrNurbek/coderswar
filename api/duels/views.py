from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import random
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_yasg import openapi

from api.duels.serializers import DuelSerializer, DuelJoinSerializer, DuelCreateSerializer, \
    DuelAssignmentsForUserSerializer
from api.utils.judge0_runner import run_code_judge0
from api.utils.utils import check_duel_end, check_duel_completion
from apps.duels.models import Duel, DuelAssignment
from apps.mainquest.models import Assignment, AssignmentStatus
from apps.userapp.models import User
class CreateDuelView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Duel yaratish (faqat duel obyektini yaratadi, topshiriq bermaydi)",
        responses={201: DuelSerializer()}
    )
    def post(self, request):
        duel = Duel.objects.create(creator=request.user)
        return Response(DuelSerializer(duel).data, status=201)


class JoinDuelView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi mavjud duelga qo'shiladi. Ikkala foydalanuvchiga ham 3 ta topshiriq biriktiriladi.",
        responses={200: openapi.Response("Duel boshlandi")}
    )
    def post(self, request, duel_id):
        user = request.user
        duel = get_object_or_404(Duel, id=duel_id, opponent__isnull=True, is_active=True)

        if duel.creator == user:
            return Response({"error": "O'zingiz yaratgan duelga qo‘shila olmaysiz."}, status=400)

        duel.opponent = user
        duel.started_at = timezone.now()
        duel.save()

        for u in [duel.creator, duel.opponent]:
            assignments = Assignment.objects.order_by('?')[:3]
            for a in assignments:
                DuelAssignment.objects.create(duel=duel, user=u, assignment=a)

        return Response({"message": "Duel boshlandi"}, status=200)

class DuelListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Bo'sh duellar ro'yxati (opponentsiz) qaytariladi",
        responses={200: DuelSerializer(many=True)}
    )
    def get(self, request):
        duels = Duel.objects.filter(opponent__isnull=True, is_active=True).exclude(creator=request.user)
        return Response(DuelSerializer(duels, many=True).data)

class DuelAssignmentsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Foydalanuvchi duelga biriktirilgan topshiriqlarini ko‘rishi",
        responses={200: DuelAssignmentsForUserSerializer(many=True)}
    )
    def get(self, request, duel_id):
        duel = get_object_or_404(Duel, id=duel_id, is_active=True)
        if request.user not in [duel.creator, duel.opponent]:
            return Response({"error": "Siz bu duel ishtirokchisi emassiz."}, status=403)

        assignments = DuelAssignment.objects.filter(duel=duel, user=request.user)
        return Response(DuelAssignmentsForUserSerializer(assignments, many=True).data)


class DuelAssignmentSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Duel topshirig'ini tekshirish. Kod to'g'ri bo'lsa, duel holati yangilanadi.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['assignment_id', 'code'],
            properties={
                'assignment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Topshiriq ID si"),
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="Foydalanuvchi C# kodi")
            }
        ),
        responses={200: openapi.Response(description="Topshiriq bajarildi va duel holati yangilandi")}
    )
    def post(self, request, duel_id):
        user = request.user
        assignment_id = request.data.get('assignment_id')
        code = request.data.get('code')

        if not assignment_id or not code:
            return Response({"error": "assignment_id va code majburiy."}, status=400)

        duel = get_object_or_404(Duel, id=duel_id, is_active=True)
        if user not in [duel.creator, duel.opponent]:
            return Response({"error": "Siz bu duel ishtirokchisi emassiz."}, status=403)

        assignment = get_object_or_404(Assignment, id=assignment_id)
        if not DuelAssignment.objects.filter(duel=duel, user=user, assignment=assignment).exists():
            return Response({"error": "Bu topshiriq sizga tegishli emas."}, status=400)

        expected_output = assignment.expected_output.strip()
        stdin = assignment.sample_input or ""
        response = run_code_judge0(code, stdin, expected_output)

        if response.get("status", {}).get("description") != "Accepted":
            return Response({"message": "Kod noto‘g‘ri."}, status=400)

        status_obj, created = AssignmentStatus.objects.get_or_create(user=user, assignment=assignment)
        if not status_obj.is_completed:
            status_obj.is_completed = True
            status_obj.save()

        check_duel_completion(duel)

        return Response({"message": "Topshiriq bajarildi", "output": response.get("stdout")}, status=200)