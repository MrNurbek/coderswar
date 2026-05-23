import random
import string

from django.core.mail import send_mail
from django.conf import settings


def generate_otp(length: int = 6) -> str:
    """Tasodifiy raqamli OTP kodi yaratish."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email: str, code: str) -> None:
    """Foydalanuvchiga OTP kodni email orqali yuborish."""
    subject = 'Coders War — Email tasdiqlash kodi'
    message = (
        f'Salom!\n\n'
        f'Tasdiqlash kodingiz: {code}\n\n'
        f'Ushbu kod 10 daqiqa davomida amal qiladi.\n\n'
        f'Agar siz ro\'yxatdan o\'tmagan bo\'lsangiz, ushbu xatni e\'tiborsiz qoldiring.\n\n'
        f'Coders War jamoasi'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_reset_password_email(email: str, code: str) -> None:
    """Parolni tiklash uchun OTP kodni email orqali yuborish."""
    subject = 'Coders War — Parolni tiklash kodi'
    message = (
        f'Salom!\n\n'
        f'Parolni tiklash kodingiz: {code}\n\n'
        f'Ushbu kod 15 daqiqa davomida amal qiladi.\n\n'
        f'Agar siz parolni tiklashni so\'ramagan bo\'lsangiz, ushbu xatni e\'tiborsiz qoldiring.\n\n'
        f'Coders War jamoasi'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def send_notification_email(email: str, title: str, body: str) -> None:
    """Umumiy bildirishnoma emaili."""
    send_mail(
        f'Coders War — {title}',
        body,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True,
    )
