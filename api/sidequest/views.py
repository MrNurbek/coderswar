
from rest_framework import generics, status, permissions ,filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import random

from api.mainquest.serializers import AssignmentSerializer, AssignmentDetailSerializer, AssignmentListSerializer
from api.sidequest.pagination import AssignmentPagination
from api.sidequest.serializers import GearItemSerializer, UserGearSerializer, CodeSubmitSerializer
from api.userapp.serializers import RegisterSerializer, UserProgressSerializer
from api.utils.judge0_runner import run_code_judge0
from apps.mainquest.models import Assignment, AssignmentStatus, UserProgress
from apps.sidequest.models import GearItem, UserGear
MCS_PATH = r"C:\Program Files\Mono\bin\mcs.bat"
MONO_PATH = r"C:\Program Files\Mono\bin\mono.exe"
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AssignmentListView(generics.ListAPIView):
    queryset = Assignment.objects.all().order_by('order')
    serializer_class = AssignmentListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AssignmentPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    @swagger_auto_schema(
        operation_summary="Barcha topshiriqlar (id, title, plan_title) [paginatsiya, qidiruv bilan]",
        operation_description=(
            "Foydalanuvchiga faqat topshiriq ID, nomi va unga tegishli rejani ko'rsatadi.\n\n"
            "**Search qilish uchun:** `?search=so'z`\n"
            "**Paginatsiya uchun:** `?page=1&page_size=10`"
        ),
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Topshiriq nomi bo‘yicha qidirish", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Sahifa raqami", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Sahifadagi elementlar soni", type=openapi.TYPE_INTEGER),
        ],
        responses={200: AssignmentListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class AssignmentDetailView(generics.RetrieveAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentDetailSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Bitta topshiriq tafsilotlari",
        operation_description="Berilgan ID bo'yicha topshiriqni to'liq tafsilotlari bilan qaytaradi.",
        responses={200: AssignmentDetailSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class AssignmentSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Topshiriqni Judge0 orqali tekshiradi, to'g'ri bo‘lsa 22 ball beradi va ehtimollik asosida gear tushiradi.",
        manual_parameters=[
            openapi.Parameter(
                'assignment_id', openapi.IN_PATH,
                description="Topshiriq ID raqami",
                type=openapi.TYPE_INTEGER
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='Foydalanuvchi kiritgan C# kodi')
            }
        ),
        responses={
            200: openapi.Response(
                description="Topshiriq muvaffaqiyatli bajarildi",
                examples={
                    "application/json": {
                        "message": "Topshiriq muvaffaqiyatli bajarildi",
                        "output": "Chiqarilgan natija",
                        "dropped_gear": "Qilich"
                    }
                }
            ),
            400: "Kod noto‘g‘ri yoki yuborilmagan",
            404: "Topshiriq topilmadi"
        }
    )
    def post(self, request, assignment_id):
        user = request.user
        code = request.data.get("code")

        if not code:
            return Response({"error": "Kod yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({"error": "Topshiriq topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        expected_output = assignment.expected_output.strip()
        stdin = assignment.sample_input or ""

        # Kodni Judge0 orqali yuborish va tekshirish
        response = run_code_judge0(code, stdin, expected_output)

        if response.get("status", {}).get("description") != "Accepted":
            return Response({"message": "Kod noto‘g‘ri yoki xatolik mavjud.", "result": response}, status=400)

        # AssignmentStatus: Ball faqat bir marta qo‘shiladi
        status_obj, created = AssignmentStatus.objects.get_or_create(user=user, assignment=assignment)

        gear_dropped = None
        if not status_obj.is_completed:
            status_obj.is_completed = True
            status_obj.earned_points = 22
            status_obj.save()

            # Foydalanuvchi reytingini oshirish
            user.rating += 22
            user.save()

            # Mavzuga ball qo‘shish yoki yaratish
            topic = assignment.plan.topic
            topic_progress, _ = UserProgress.objects.get_or_create(user=user, topic=topic)
            topic_progress.score += 22
            topic_progress.save()

            # Aslaxa tushurish
            gear_dropped = self.try_drop_gear(user)

        return Response({
            "message": "Topshiriq muvaffaqiyatli bajarildi",
            "output": response.get("stdout"),
            "dropped_gear": gear_dropped or "Hech narsa tushmadi"
        }, status=200)

    def try_drop_gear(self, user):
        drop_chance = 0
        quality_pool = []

        if user.rating < 3300:
            drop_chance = 18
            quality_pool = ['basic']
        elif 3300 <= user.rating < 5720:
            drop_chance = 20
            quality_pool = ['basic', 'medium']
        else:
            drop_chance = 22
            quality_pool = ['basic', 'medium', 'rare']

        roll = random.randint(1, 100)
        if roll <= drop_chance:
            gears = GearItem.objects.filter(quality__in=quality_pool)

            if user.character:
                name = user.character.name
                if name == "Jangchi":
                    gears = gears.exclude(type__in=['magic', 'spear'])
                elif name in ["Ritsar", "Ayol ritsar"]:
                    gears = gears.exclude(type__in=['magic', 'spear'])
                elif name == "Sarguzashtchi":
                    gears = gears.exclude(type__in=['sword', 'magic'])
                elif name == "Sehrgar":
                    gears = gears.exclude(type__in=['sword', 'spear'])

            if gears.exists():
                gear = random.choice(list(gears))
                UserGear.objects.create(user=user, gear=gear)
                return gear.name
        return None



class DropGearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        score = user.rating

        # Define drop chance
        if score < 3300:
            chance = 18
            quality_pool = ['basic']
        elif 3300 <= score < 5720:
            chance = 20
            quality_pool = ['basic', 'medium']
        else:
            chance = 22
            quality_pool = ['basic', 'medium', 'rare']

        roll = random.randint(1, 100)
        if roll <= chance:
            gears = GearItem.objects.filter(quality__in=quality_pool)
            if user.character.name == "Jangchi":
                gears = gears.exclude(type__in=['magic', 'spear'])
            elif user.character.name == "Ritsar" or user.character.name == "Ayol ritsar":
                gears = gears.exclude(type__in=['magic', 'spear'])
            elif user.character.name == "Sarguzashtchi":
                gears = gears.exclude(type__in=['sword', 'magic'])
            elif user.character.name == "Sehrgar":
                gears = gears.exclude(type__in=['sword', 'spear'])

            gear = random.choice(list(gears))
            UserGear.objects.create(user=user, gear=gear)
            return Response({"status": "dropped", "item": GearItemSerializer(gear).data})
        return Response({"status": "miss", "message": "Aslaxa tushmadi."})

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        gears = UserGear.objects.filter(user=user)
        completed_assignments = AssignmentStatus.objects.filter(user=user, is_completed=True)
        progress = UserProgress.objects.filter(user=user)

        return Response({
            "user": RegisterSerializer(user).data,
            "gears": UserGearSerializer(gears, many=True).data,
            "assignments_completed": completed_assignments.count(),
            "rating": user.rating,
            "topics_progress": UserProgressSerializer(progress, many=True).data
        })
