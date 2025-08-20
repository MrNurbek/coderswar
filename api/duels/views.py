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
from api.duels.utils import check_duel_expired
from api.utils.judge0_runner import run_code_judge0
from api.utils.utils import check_duel_end, check_duel_completion
from apps.duels.models import Duel, DuelAssignment
from apps.mainquest.models import Assignment, AssignmentStatus
from apps.userapp.models import User

# class CreateDuelView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @swagger_auto_schema(
#         operation_description="Duel yaratish (faqat duel obyektini yaratadi, topshiriq bermaydi)",
#         responses={201: DuelSerializer()}
#     )
#     def post(self, request):
#         duel = Duel.objects.create(creator=request.user)
#         return Response(DuelSerializer(duel).data, status=201)
class CreateDuelView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Duel yaratish (faqat duel obyektini yaratadi, topshiriq bermaydi)",
        responses={201: DuelSerializer()}
    )
    def post(self, request):
        has_unfinished = Duel.objects.filter(
            creator=request.user,
            is_active=True,
            winner__isnull=True,
        ).exists()

        if has_unfinished:
            return Response(
                {"detail": "Sizda tugallanmagan 1 ta duel bor. Yangi duel yaratishdan avval uni yakunlang."},
                status=status.HTTP_409_CONFLICT,
            )

        duel = Duel.objects.create(creator=request.user)
        return Response(DuelSerializer(duel).data, status=status.HTTP_201_CREATED)

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
        check_duel_expired(duel)
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

        duel_assignment = DuelAssignment.objects.get(duel=duel, user=user, assignment=assignment)
        if not duel_assignment.is_completed:
            duel_assignment.is_completed = True
            duel_assignment.save()

        check_duel_completion(duel)

        return Response({"message": "Topshiriq bajarildi", "output": response.get("stdout")}, status=200)

class DuelStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Duel holatini ko‘rish: foydalanuvchilar, ishlangan topshiriqlar va vaqt holati bilan.",
        manual_parameters=[
            openapi.Parameter(
                'duel_id',
                openapi.IN_PATH,
                description="Duel ID raqami",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "duel_id": openapi.Schema(type=openapi.TYPE_INTEGER),

                    # Vaqtlar — frontendga qulay formatlar:
                    "started_at_iso": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME,
                        description="Boshlanish vaqti (local time, ISO 8601, masalan: 2025-08-20T14:32:10+05:00)"
                    ),
                    "started_at_text": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Boshlanish vaqti matn ko‘rinishida (dd.mm.yyyy HH:MM), masalan: 20.08.2025 14:32"
                    ),
                    "started_at_unix": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Boshlanish vaqti UNIX timestamp (soniyada)"
                    ),

                    # Orqaga moslik uchun (xohlasangiz olib tashlashingiz mumkin):
                    "started_at": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME,
                        description="(Legacy) boshlanish vaqti; avval qaytarilgan raw datetime/ISO"
                    ),

                    "elapsed_time_seconds": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Duel boshlanganidan beri o‘tgan vaqt (sekundlarda)"
                    ),
                    "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "winner_id": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="G‘olib foydalanuvchi ID si (agar mavjud bo‘lsa)"
                    ),
                    "creator": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "profile_image": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                            "assignments": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "assignment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "title": openapi.Schema(type=openapi.TYPE_STRING),
                                        "is_completed": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    }
                                )
                            )
                        }
                    ),
                    "opponent": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        nullable=True,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                            "profile_image": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                            "assignments": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "assignment_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "title": openapi.Schema(type=openapi.TYPE_STRING),
                                        "is_completed": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    }
                                )
                            )
                        }
                    ),
                }
            ),
            403: openapi.Response(description="Siz bu duel ishtirokchisi emassiz."),
            404: openapi.Response(description="Duel topilmadi."),
        }
    )
    def get(self, request, duel_id):
        duel = get_object_or_404(Duel, id=duel_id)

        if request.user not in [duel.creator, duel.opponent]:
            return Response({"error": "Siz bu duel ishtirokchisi emassiz."}, status=403)

        # Duel 15 daqiqa o'tgan bo‘lsa avtomatik yopamiz (ichki qoidangizga ko‘ra)
        check_duel_expired(duel)

        def get_user_data(user):
            assignments = DuelAssignment.objects.filter(duel=duel, user=user)
            result = []
            for da in assignments:
                result.append({
                    "assignment_id": da.assignment.id,
                    "title": da.assignment.title,
                    "is_completed": da.is_completed
                })
            return {
                "id": user.id,
                "full_name": user.full_name,
                "profile_image": request.build_absolute_uri(user.profile_image.url) if getattr(user, "profile_image", None) else None,
                "assignments": result
            }

        # Vaqt hisoblash
        now = timezone.now()
        start_time = duel.started_at or duel.created_at
        elapsed_seconds = int((now - start_time).total_seconds())

        # Frontendga qulay formatlar (Django TIME_ZONE bo‘yicha)
        local_start = timezone.localtime(start_time)
        started_at_iso = local_start.isoformat()                 # 2025-08-20T14:32:10+05:00
        started_at_text = local_start.strftime('%d.%m.%Y %H:%M') # 20.08.2025 14:32
        started_at_unix = int(local_start.timestamp())           # 1692525130

        return Response({
            "duel_id": duel.id,
            "started_at_iso": started_at_iso,
            "started_at_text": started_at_text,
            "started_at_unix": started_at_unix,
            # Orqaga moslik: avval bo‘lgani kabi raw datetime/ISO (agar serializer/renderer ISOga aylantirsa)
            "started_at": duel.started_at,
            "elapsed_time_seconds": elapsed_seconds,
            "is_active": duel.is_active,
            "creator": get_user_data(duel.creator),
            "opponent": get_user_data(duel.opponent) if duel.opponent else None,
            "winner_id": duel.winner.id if duel.winner else None
        })