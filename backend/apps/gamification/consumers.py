"""
Django Channels WebSocket consumer — Duel real-vaqt musobaqasi.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class DuelConsumer(AsyncWebsocketConsumer):
    """
    ws://host/ws/duel/<room_id>/
    Xabar turlari:
      client → server:  {type: 'code_update', code: '...'}
                        {type: 'submit',      code: '...'}
                        {type: 'ready'}
                        {type: 'surrender'}
      server → client:  {type: 'connected',        room_id, user}
                        {type: 'opponent_code',     code}
                        {type: 'opponent_ready'}
                        {type: 'submission_received', submission_id}
                        {type: 'opponent_submitted'}
                        {type: 'duel_result',       winner, win_pts, lose_pts, scores}
                        {type: 'error',             message}
    """

    async def connect(self):
        self.room_id    = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'duel_{self.room_id}'
        self.user       = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        duel = await self.get_duel()
        if not duel:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'type':    'connected',
            'room_id': self.room_id,
            'user':    self.user.username,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error('Noto\'g\'ri JSON format.')
            return

        msg_type = data.get('type')

        if msg_type == 'code_update':
            # Raqibga kodni real-vaqtda uzatish (faqat raqibga)
            await self.channel_layer.group_send(self.group_name, {
                'type':   'opponent_code_msg',
                'sender': self.user.username,
                'code':   data.get('code', ''),
            })

        elif msg_type == 'submit':
            code = data.get('code', '')
            await self.save_code(code)

            # Raqibga "opponent submitted" xabarini yuborish
            await self.channel_layer.group_send(self.group_name, {
                'type':   'opponent_submitted_msg',
                'sender': self.user.username,
            })

            # Celery orqali Judge0 ga yuborish
            submission_id = await self.create_submission(code)
            if submission_id:
                from apps.courses.tasks import submit_to_judge0
                submit_to_judge0.delay(submission_id)
                await self.send(text_data=json.dumps({
                    'type':          'submission_received',
                    'submission_id': submission_id,
                }))

        elif msg_type == 'ready':
            await self.channel_layer.group_send(self.group_name, {
                'type':   'opponent_ready_msg',
                'sender': self.user.username,
            })

        elif msg_type == 'surrender':
            # Taslim bo'lish — raqib g'olib
            result = await self.do_surrender()
            if result:
                winner, win_pts, lose_pts = result
                await self.channel_layer.group_send(self.group_name, {
                    'type':     'duel_result_msg',
                    'winner':   winner,
                    'win_pts':  win_pts,
                    'lose_pts': lose_pts,
                    'scores':   {},
                })

        else:
            await self.send_error(f'Noma\'lum xabar turi: {msg_type}')

    # ── Channel layer handlers ────────────────────────────────────────────────

    async def opponent_code_msg(self, event):
        """Raqib kodini yuborish (faqat boshqa foydalanuvchiga)."""
        if event['sender'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'opponent_code',
                'code': event['code'],
            }))

    async def opponent_ready_msg(self, event):
        if event['sender'] != self.user.username:
            await self.send(text_data=json.dumps({'type': 'opponent_ready'}))

    async def opponent_submitted_msg(self, event):
        if event['sender'] != self.user.username:
            await self.send(text_data=json.dumps({'type': 'opponent_submitted'}))

    async def duel_result_msg(self, event):
        """G'olib aniqlanganda ikkala o'yinchiga yuborish."""
        await self.send(text_data=json.dumps({
            'type':     'duel_result',
            'winner':   event.get('winner'),
            'win_pts':  event.get('win_pts', 0),
            'lose_pts': event.get('lose_pts', 0),
            'scores':   event.get('scores', {}),
        }))

    # ── DB helpers ────────────────────────────────────────────────────────────

    @database_sync_to_async
    def get_duel(self):
        from .models import Duel
        try:
            return Duel.objects.get(room_id=self.room_id)
        except Duel.DoesNotExist:
            return None

    @database_sync_to_async
    def save_code(self, code: str):
        """Foydalanuvchi kodini Duel modeliga saqlash."""
        from .models import Duel
        try:
            duel = Duel.objects.get(room_id=self.room_id)
            if duel.challenger_id == self.user.id:
                duel.challenger_code = code
                duel.save(update_fields=['challenger_code'])
            else:
                duel.opponent_code = code
                duel.save(update_fields=['opponent_code'])
        except Duel.DoesNotExist:
            pass

    @database_sync_to_async
    def create_submission(self, code: str):
        """Duel submission yaratish va Judge0 ga yuborish uchun ID qaytarish."""
        from .models import Duel
        from apps.courses.models import Submission
        try:
            duel = Duel.objects.select_related('task').get(room_id=self.room_id)
            if not duel.task:
                return None
            sub = Submission.objects.create(
                student=self.user,
                task=duel.task,
                code=code,
                language='csharp',
            )
            return sub.id
        except Exception:
            return None

    @database_sync_to_async
    def do_surrender(self):
        """Taslim bo'lish — raqib g'olib deb belgilanadi."""
        from .models import Duel
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            duel = Duel.objects.get(room_id=self.room_id)
            if duel.status != Duel.Status.IN_PROGRESS:
                return None
            # G'olib = raqib
            if duel.challenger_id == self.user.id:
                winner = duel.opponent
                loser  = duel.challenger
            else:
                winner = duel.challenger
                loser  = duel.opponent
            if not winner or not loser:
                return None
            win_pts, lose_pts = duel.finish(winner, loser)
            return winner.username, win_pts, lose_pts
        except Exception:
            return None

    async def send_error(self, message: str):
        await self.send(text_data=json.dumps({'type': 'error', 'message': message}))


# ── Submission natijasidan Duel g'olibni aniqlash ─────────────────────────────
# Bu funksiya apps/courses/tasks.py dan chaqiriladi

def notify_duel_result(submission_id: int):
    """
    Submission PASSED bo'lganda, agar duel bo'lsa — g'olibni belgilash
    va WebSocket orqali xabar yuborish.
    Celery task'dan sinxron chaqiriladi.
    """
    from apps.courses.models import Submission
    from apps.gamification.models import Duel
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    try:
        sub  = Submission.objects.select_related('student', 'task').get(id=submission_id)
        task = sub.task

        # Bu task'ga bog'liq IN_PROGRESS duel bormi?
        from django.db.models import Q
        duel = Duel.objects.filter(
            task=task,
            status=Duel.Status.IN_PROGRESS,
        ).filter(
            Q(challenger=sub.student) | Q(opponent=sub.student)
        ).first()

        if not duel:
            return

        # G'olib — birinchi PASSED bo'lgan
        if duel.challenger_id == sub.student_id:
            winner = duel.challenger
            loser  = duel.opponent
            duel.challenger_score = sub.score_awarded
        else:
            winner = duel.opponent
            loser  = duel.challenger
            duel.opponent_score = sub.score_awarded

        if not winner or not loser:
            return

        win_pts, lose_pts = duel.finish(winner, loser)

        # WebSocket orqali natijani yuborish
        channel_layer = get_channel_layer()
        group_name    = f'duel_{duel.room_id}'
        async_to_sync(channel_layer.group_send)(group_name, {
            'type':     'duel_result_msg',
            'winner':   winner.username,
            'win_pts':  win_pts,
            'lose_pts': lose_pts,
            'scores': {
                'challenger': duel.challenger_score,
                'opponent':   duel.opponent_score,
            },
        })

    except Exception:
        pass
