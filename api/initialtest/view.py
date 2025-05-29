from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from api.initialtest.serializer import InitialTestSerializer, InitialTestSubmitSerializer
from apps.initialtest.models import InitialTest, InitialTestAnswer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class InitialTestListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: InitialTestSerializer(many=True)})
    def get(self, request):
        tests = InitialTest.objects.all().order_by('order')[:10]
        serializer = InitialTestSerializer(tests, many=True)
        return Response(serializer.data)

class InitialTestSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Boshlang‘ich test natijalarini topshirish",
        operation_description="""
10 ta boshlang‘ich test savoliga foydalanuvchi tanlagan javob variantlarini yuboradi. 
Har bir javob `answer_id` ko‘rinishida yuboriladi. 
Server to‘g‘ri javoblar sonini hisoblab qaytaradi.
""",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["answers"],
            properties={
                "answers": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "answer_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Javob varianti IDsi")
                        },
                        required=["answer_id"]
                    ),
                    description="Foydalanuvchi tanlagan 10 ta variant ID'lar ro'yxati"
                )
            },
            example={
                "answers": [
                    {"answer_id": 12},
                    {"answer_id": 15},
                    {"answer_id": 18},
                    {"answer_id": 21},
                    {"answer_id": 24},
                    {"answer_id": 27},
                    {"answer_id": 30},
                    {"answer_id": 33},
                    {"answer_id": 36},
                    {"answer_id": 39}
                ]
            }
        ),
        responses={
            200: openapi.Response(
                description="Test natijasi",
                examples={
                    "application/json": {
                        "status": "ok",
                        "correct_answers": 7,
                        "total": 10
                    }
                }
            ),
            400: "Yuborilgan ma'lumot noto'g'ri",
        }
    )
    def post(self, request):
        serializer = InitialTestSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data['answers']

        correct = 0
        for answer in answers:
            try:
                answer_id = int(answer['answer_id'])
                ans = InitialTestAnswer.objects.get(id=answer_id)
                if ans.is_correct:
                    correct += 1
            except (InitialTestAnswer.DoesNotExist, KeyError, ValueError):
                continue

        return Response({
            "status": "ok",
            "correct_answers": correct,
            "total": len(answers)
        })

