import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ContactSerializer, EmailSubmissionSerializer

# Telegram konfiguratsiyasi
TELEGRAM_BOT_TOKEN = '8120112271:AAFt_eO0bsGXlxsd7McY5K_96RRjcZ7lwDE'
TELEGRAM_CHAT_ID = '314635555'

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    print("Telegram javobi:", response.text)
    return response.ok

class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ContactSerializer,
        responses={
            200: openapi.Response(description="Xabar yuborildi"),
            400: "Xato ma'lumotlar",
            500: "Telegram xatosi"
        }
    )
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            full_name = data['full_name']
            email = data['email']
            phone = data['phone_number']
            text = data['message']
            user = request.user

            message = (
                f"📥 Yangi murojaat:\n"
                f"👤 Username: {user.username}\n"
                f"🧑 F.I.Sh.: {full_name}\n"
                f"📧 Email: {email}\n"
                f"📞 Tel: {phone}\n"
                f"✉️ Xabar:\n{text}"
            )

            sent = send_telegram_message(message)

            if sent:
                return Response({"message": "Telegramga yuborildi ✅"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "❌ Telegramga yuborishda xatolik yuz berdi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class EmailSubmissionView(APIView):
    @swagger_auto_schema(
        request_body=EmailSubmissionSerializer,
        responses={201: EmailSubmissionSerializer()}
    )
    def post(self, request):
        serializer = EmailSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)