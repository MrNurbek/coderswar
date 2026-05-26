import uuid
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Duel, Clan, ClanMembership, ClanWar, ClanChat, Badge, UserBadge, Equipment, UserEquipment
from .serializers import (
    DuelSerializer, DuelCreateSerializer,
    ClanSerializer, ClanDetailSerializer, ClanMembershipSerializer,
    ClanWarSerializer, ClanWarCreateSerializer,
    ClanChatSerializer, ClanChatCreateSerializer,
    BadgeSerializer, UserBadgeSerializer,
    EquipmentSerializer, UserEquipmentSerializer,
)


# ─── Duel ────────────────────────────────────────────────────────────────────

class DuelViewSet(viewsets.ModelViewSet):
    serializer_class   = DuelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['status', 'duel_type']
    ordering_fields    = ['-created_at']

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        return Duel.objects.filter(
            Q(challenger=user) | Q(opponent=user)
        ).select_related('challenger', 'opponent', 'winner', 'task')

    def get_serializer_class(self):
        if self.action == 'create':
            return DuelCreateSerializer
        return DuelSerializer

    def create(self, request, *args, **kwargs):
        from apps.courses.models import Task
        import random as _rnd

        s = DuelCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        duel_type = s.validated_data.get('duel_type', 'algorithmic')
        task_id   = s.validated_data.get('task')

        # 1) Mavjud kutish holati duelga qo'shilish (matchmaking)
        waiting = Duel.objects.filter(
            status=Duel.Status.WAITING,
            duel_type=duel_type,
        ).exclude(challenger=request.user).first()

        if waiting:
            waiting.opponent   = request.user
            waiting.status     = Duel.Status.IN_PROGRESS
            from django.utils import timezone
            waiting.started_at = timezone.now()
            waiting.save(update_fields=['opponent', 'status', 'started_at'])
            return Response(DuelSerializer(waiting).data, status=status.HTTP_200_OK)

        # 2) Yangi duel yaratish
        task = None
        if task_id:
            task = Task.objects.filter(id=task_id, is_active=True).first()
        if not task:
            # Random task — boshlang'ich daraja exercise
            tasks = list(Task.objects.filter(
                is_active=True, level='beginner', task_category='exercise'
            ).values_list('id', flat=True))
            if tasks:
                task = Task.objects.get(id=_rnd.choice(tasks))

        room_id = str(uuid.uuid4())[:12].upper()
        duel = Duel.objects.create(
            challenger=request.user,
            task=task,
            duel_type=duel_type,
            room_id=room_id,
            rating_reward=15,
        )
        return Response(DuelSerializer(duel).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Raqibni qo'shish."""
        duel = self.get_object()
        if duel.status != Duel.Status.WAITING:
            return Response({'detail': 'Duel kutilmayapti.'}, status=400)
        if duel.challenger == request.user:
            return Response({'detail': 'O\'z duelingizga kira olmaysiz.'}, status=400)

        duel.opponent = request.user
        duel.status   = Duel.Status.IN_PROGRESS
        from django.utils import timezone
        duel.started_at = timezone.now()
        duel.save(update_fields=['opponent', 'status', 'started_at'])
        return Response(DuelSerializer(duel).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        duel = self.get_object()
        if duel.challenger != request.user:
            return Response({'detail': 'Faqat boshlagan shaxs bekor qila oladi.'}, status=403)
        if duel.status != Duel.Status.WAITING:
            return Response({'detail': 'Bekor qilib bo\'lmaydi.'}, status=400)
        duel.status = Duel.Status.CANCELLED
        duel.save(update_fields=['status'])
        return Response({'detail': 'Duel bekor qilindi.'})


# ─── Clan ────────────────────────────────────────────────────────────────────

class ClanViewSet(viewsets.ModelViewSet):
    serializer_class   = ClanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['is_active']
    ordering_fields    = ['-rating_score']

    def get_queryset(self):
        return Clan.objects.filter(is_active=True).select_related('leader')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClanDetailSerializer
        return ClanSerializer

    def create(self, request, *args, **kwargs):
        """Yangi klan yaratish — yaratuvchi avtomatik Leader bo'ladi."""
        # Foydalanuvchi allaqachon klanga a'zo bo'lmasligi kerak
        if ClanMembership.objects.filter(user=request.user).exists():
            return Response({'detail': 'Siz allaqachon klanga a\'zosiz.'}, status=400)

        s = ClanSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)

        clan = s.save(leader=request.user)
        ClanMembership.objects.create(
            clan=clan, user=request.user, role=ClanMembership.Role.LEADER
        )
        return Response(ClanDetailSerializer(clan, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        clan = self.get_object()
        if ClanMembership.objects.filter(user=request.user).exists():
            return Response({'detail': 'Allaqachon klanga a\'zosiz.'}, status=400)

        ClanMembership.objects.create(clan=clan, user=request.user)

        # Liderga yangi a'zo haqida bildiruv yuborish
        try:
            from apps.social.models import Notification
            leader_mb = ClanMembership.objects.filter(
                clan=clan, role=ClanMembership.Role.LEADER
            ).select_related('user').first()
            if leader_mb and leader_mb.user != request.user:
                full_name = request.user.get_full_name() or request.user.username
                Notification.objects.create(
                    user       = leader_mb.user,
                    title      = '👥 Yangi a\'zo qo\'shildi!',
                    message    = (
                        f'{full_name} "{clan.name}" klanga qo\'shildi. '
                        f'Hozir klaningizda {clan.memberships.count()} a\'zo bor.'
                    ),
                    notif_type = 'clan',
                    link       = '/clan.html',
                )
        except Exception:
            pass

        return Response({'detail': f'{clan.name} klanga qo\'shildingiz.'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        clan = self.get_object()
        if clan.leader == request.user:
            return Response({'detail': 'Lider klanini tark eta olmaydi. Avval liderni o\'zgartiring.'}, status=400)
        deleted, _ = ClanMembership.objects.filter(clan=clan, user=request.user).delete()
        if not deleted:
            return Response({'detail': 'A\'zolik topilmadi.'}, status=404)

        # Liderga a'zo chiqib ketgani haqida bildiruv yuborish
        try:
            from apps.social.models import Notification
            leader_mb = ClanMembership.objects.filter(
                clan=clan, role=ClanMembership.Role.LEADER
            ).select_related('user').first()
            if leader_mb:
                full_name = request.user.get_full_name() or request.user.username
                Notification.objects.create(
                    user       = leader_mb.user,
                    title      = '👤 A\'zo klanidan chiqdi',
                    message    = (
                        f'{full_name} "{clan.name}" klanidan chiqdi. '
                        f'Hozir klaningizda {clan.memberships.count()} a\'zo qoldi.'
                    ),
                    notif_type = 'clan',
                    link       = '/clan.html',
                )
        except Exception:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def chat(self, request, pk=None):
        clan = self.get_object()
        messages = ClanChat.objects.filter(clan=clan).select_related('user').order_by('created_at')
        return Response(ClanChatSerializer(messages, many=True).data)

    @action(detail=True, methods=['post'], url_path='chat/send')
    def send_message(self, request, pk=None):
        clan = self.get_object()
        if not ClanMembership.objects.filter(clan=clan, user=request.user).exists():
            return Response({'detail': 'Faqat a\'zolar xabar yoza oladi.'}, status=403)

        s = ClanChatCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        msg = s.save(clan=clan, user=request.user)
        return Response(ClanChatSerializer(msg).data, status=status.HTTP_201_CREATED)


# ─── ClanWar ─────────────────────────────────────────────────────────────────

class ClanWarViewSet(viewsets.ModelViewSet):
    """
    Klanlar urushi.
      create  → lider boshqa klanga challenge yuboradi (status=scheduled)
      accept  → raqib klan lideri qabul qiladi (status=in_progress, started_at=now)
      finish  → g'olibni belgilash, klanlarga ball berish
      cancel  → bekor qilish
    """
    serializer_class   = ClanWarSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['status', 'war_type']

    def get_queryset(self):
        return ClanWar.objects.select_related('clan1', 'clan2', 'winner').order_by('-scheduled_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return ClanWarCreateSerializer
        return ClanWarSerializer

    def create(self, request, *args, **kwargs):
        """Lider boshqa klanga challenge yuboradi."""
        # Foydalanuvchi lider bo'lishi kerak
        membership = ClanMembership.objects.filter(
            user=request.user, role=ClanMembership.Role.LEADER
        ).first()
        if not membership:
            return Response({'detail': 'Faqat klan lideri urush boshlay oladi.'}, status=403)

        s = ClanWarCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        opponent_clan = s.validated_data['clan2']
        if membership.clan == opponent_clan:
            return Response({'detail': 'O\'z klangizga challenge yubora olmaysiz.'}, status=400)

        from django.utils import timezone
        war = ClanWar.objects.create(
            clan1        = membership.clan,
            clan2        = opponent_clan,
            war_type     = s.validated_data.get('war_type', ClanWar.WarType.ALGORITHMIC),
            scheduled_at = s.validated_data['scheduled_at'],
            status       = ClanWar.Status.SCHEDULED,
        )

        # Bildiruv — raqib klan lideriga
        try:
            from apps.social.models import Notification
            opp_leader = ClanMembership.objects.filter(
                clan=opponent_clan, role=ClanMembership.Role.LEADER
            ).first()
            if opp_leader:
                Notification.objects.create(
                    user       = opp_leader.user,
                    title      = '⚔️ Klan urushi taklifi!',
                    message    = (
                        f'{membership.clan.name} klani sizga klan urushiga challenge yubordi! '
                        f'Turi: {war.get_war_type_display()}, '
                        f'Sana: {war.scheduled_at.strftime("%d.%m.%Y %H:%M")}'
                    ),
                    notif_type = 'clan',
                    link       = '/clan.html',
                )
        except Exception:
            pass

        return Response(ClanWarSerializer(war).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Raqib klan lideri urushni qabul qiladi."""
        war = self.get_object()
        if war.status != ClanWar.Status.SCHEDULED:
            return Response({'detail': 'Bu urush qabul qilib bo\'lmaydi.'}, status=400)

        membership = ClanMembership.objects.filter(
            user=request.user, clan=war.clan2, role=ClanMembership.Role.LEADER
        ).first()
        if not membership:
            return Response({'detail': 'Faqat raqib klan lideri qabul qila oladi.'}, status=403)

        from django.utils import timezone
        war.status     = ClanWar.Status.IN_PROGRESS
        war.started_at = timezone.now()
        war.save(update_fields=['status', 'started_at'])
        return Response(ClanWarSerializer(war).data)

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """
        Urushni yakunlash va g'olibni belgilash.
        Body: { winner_clan_id: N, clan1_score: X, clan2_score: Y }
        """
        war = self.get_object()
        if war.status != ClanWar.Status.IN_PROGRESS:
            return Response({'detail': 'Urush davom etmayapti.'}, status=400)

        winner_id  = request.data.get('winner_clan_id')
        clan1_score = int(request.data.get('clan1_score', 0))
        clan2_score = int(request.data.get('clan2_score', 0))

        try:
            winner_clan = Clan.objects.get(id=winner_id)
        except Clan.DoesNotExist:
            return Response({'detail': 'G\'olib klan topilmadi.'}, status=400)

        if winner_clan not in (war.clan1, war.clan2):
            return Response({'detail': 'G\'olib ushbu urushda qatnashmagan.'}, status=400)

        from django.utils import timezone
        war.winner      = winner_clan
        war.clan1_score = clan1_score
        war.clan2_score = clan2_score
        war.status      = ClanWar.Status.COMPLETED
        war.ended_at    = timezone.now()
        war.save(update_fields=['winner', 'clan1_score', 'clan2_score', 'status', 'ended_at'])

        # G'olib klanning rating balini oshirish (+50)
        reward = 50
        winner_clan.rating_score += reward
        winner_clan.save(update_fields=['rating_score'])

        # Bildiruv — ikkala klan a'zolariga
        try:
            from apps.social.models import Notification
            winner_members = ClanMembership.objects.filter(clan=winner_clan).select_related('user')
            loser_clan     = war.clan2 if winner_clan == war.clan1 else war.clan1
            loser_members  = ClanMembership.objects.filter(clan=loser_clan).select_related('user')

            for m in winner_members:
                Notification.objects.create(
                    user=m.user, title='🏆 Klan urushida g\'alaba!',
                    message=f'{winner_clan.name} klani klan urushida g\'olib chiqdi! +{reward} ball.',
                    notif_type='clan', link='/clan.html',
                )
            for m in loser_members:
                Notification.objects.create(
                    user=m.user, title='⚔️ Klan urushi yakunlandi',
                    message=f'Afsuski, {winner_clan.name} klani g\'olib chiqdi. Qo\'lingizdan kelganini qildingiz!',
                    notif_type='clan', link='/clan.html',
                )
        except Exception:
            pass

        return Response(ClanWarSerializer(war).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Urushni bekor qilish (faqat scheduled holati)."""
        war = self.get_object()
        if war.status != ClanWar.Status.SCHEDULED:
            return Response({'detail': 'Bekor qilib bo\'lmaydi.'}, status=400)

        # Faqat qatnashuvchi klan liderlari bekor qila oladi
        is_leader = ClanMembership.objects.filter(
            user=request.user,
            clan__in=[war.clan1, war.clan2],
            role=ClanMembership.Role.LEADER,
        ).exists()
        if not is_leader:
            return Response({'detail': 'Faqat klan lideri bekor qila oladi.'}, status=403)

        war.status = ClanWar.Status.CANCELLED
        war.save(update_fields=['status'])
        return Response({'detail': 'Urush bekor qilindi.'})


# ─── Leaderboard ─────────────────────────────────────────────────────────────

class LeaderboardView(generics.ListAPIView):
    """Talabalar reytingi — top 100."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        from apps.users.models import StudentProfile
        from apps.users.serializers import StudentProfileSerializer

        group_id = request.query_params.get('group')
        qs = StudentProfile.objects.select_related('user').order_by('-rating_score')[:100]

        if group_id:
            qs = StudentProfile.objects.filter(
                user__group_memberships__group_id=group_id
            ).select_related('user').order_by('-rating_score')[:100]

        data = StudentProfileSerializer(qs, many=True, context={'request': request}).data
        for i, item in enumerate(data):
            item['rank'] = i + 1
        return Response(data)


class ClanLeaderboardView(generics.ListAPIView):
    """Klanlar reytingi."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ClanSerializer

    def get_queryset(self):
        return Clan.objects.filter(is_active=True).order_by('-rating_score')[:50]


# ─── Badge ────────────────────────────────────────────────────────────────────

class BadgeListView(generics.ListAPIView):
    queryset           = Badge.objects.filter(is_active=True)
    serializer_class   = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class MyBadgesView(generics.ListAPIView):
    serializer_class   = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).select_related('badge')


# ─── Equipment / Inventory ────────────────────────────────────────────────────

class InventoryView(generics.ListAPIView):
    """Foydalanuvchining barcha qurol-aslahalari (inventar)."""
    serializer_class   = UserEquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserEquipment.objects.filter(
            user=self.request.user
        ).select_related('equipment').order_by('-acquired_at')


class EquipItemView(generics.GenericAPIView):
    """Qurolni kiyish / yechish."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action', 'equip')  # 'equip' | 'unequip'
        try:
            if action == 'equip':
                ue = UserEquipment.equip(request.user, pk)
            else:
                UserEquipment.unequip(request.user, pk)
                ue = UserEquipment.objects.select_related('equipment').get(id=pk, user=request.user)
            return Response(UserEquipmentSerializer(ue).data)
        except UserEquipment.DoesNotExist:
            return Response({'detail': 'Topilmadi.'}, status=404)


class EquippedBonusView(generics.GenericAPIView):
    """Joriy kiyilgan jihozlar va umumiy bonus."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = UserEquipment.objects.filter(
            user=request.user, is_equipped=True
        ).select_related('equipment')
        attack, defense = UserEquipment.get_equipped_bonuses(request.user)
        return Response({
            'items':   UserEquipmentSerializer(items, many=True).data,
            'total_attack_bonus':  attack,
            'total_defense_bonus': defense,
        })
