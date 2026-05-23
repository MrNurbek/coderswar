from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Module, Topic, TopicLevelContent,
    LevelTest, LevelTestQuestion, StudentLevelTestResult,
    StudentLevelProgress, TopicScore,
    Task, Submission, DiagnosticTest, ReflectionJournal,
)
from .serializers import (
    ModuleSerializer,
    TopicSerializer, TopicDetailSerializer, TopicMiniSerializer,
    TopicLevelContentSerializer, TopicLevelContentStudentSerializer,
    StudentLevelProgressSerializer, StudentLevelProgressUpdateSerializer,
    LevelTestSerializer, LevelTestTeacherSerializer,
    LevelTestSubmitSerializer, StudentLevelTestResultSerializer,
    TopicScoreSerializer, TopicScoreTeacherUpdateSerializer,
    TopicScoreFaProjectUpdateSerializer, TopicScoreRePeerUpdateSerializer,
    TaskSerializer, TaskStudentSerializer,
    SubmissionSerializer, SubmissionCreateSerializer,
    DiagnosticTestSerializer, DiagnosticTestSubmitSerializer,
    ReflectionJournalSerializer,
)
from .services import calculate_diagnostic_level


# ─── Permissions ─────────────────────────────────────────────────────────────

class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('teacher', 'admin', 'superadmin')


class IsStudentOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'


# ─── Module ──────────────────────────────────────────────────────────────────

class ModuleListView(generics.ListAPIView):
    queryset           = Module.objects.filter(is_active=True)
    serializer_class   = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]


# ─── Topic ───────────────────────────────────────────────────────────────────

class TopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields   = ['module', 'difficulty', 'is_active']
    search_fields      = ['title', 'description']
    ordering_fields    = ['number', 'order']

    def get_queryset(self):
        return Topic.objects.select_related('module').filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TopicDetailSerializer
        return TopicSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def my_score(self, request, pk=None):
        topic = self.get_object()
        try:
            score = TopicScore.objects.get(student=request.user, topic=topic)
            return Response(TopicScoreSerializer(score).data)
        except TopicScore.DoesNotExist:
            return Response({'detail': 'Ball mavjud emas.'}, status=404)


# ─── TopicLevelContent (O'qituvchi boshqaradi) ───────────────────────────────

class TopicLevelContentViewSet(viewsets.ModelViewSet):
    """
    Mavzu daraja kontentini boshqarish.
    GET  — barcha foydalanuvchilar uchun (talaba serializer bilan)
    POST/PUT/PATCH/DELETE — faqat o'qituvchilar uchun
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        topic_id = self.kwargs.get('topic_pk')
        return TopicLevelContent.objects.filter(topic_id=topic_id).order_by('level')

    def get_serializer_class(self):
        if self.request.user.role in ('teacher', 'admin', 'superadmin'):
            return TopicLevelContentSerializer
        return TopicLevelContentStudentSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        topic_id = self.kwargs.get('topic_pk')
        serializer.save(topic_id=topic_id, created_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-level/(?P<level>[a-z]+)')
    def by_level(self, request, topic_pk=None, level=None):
        """Bitta daraja kontentini olish: /topics/{id}/contents/by-level/beginner/"""
        try:
            content = self.get_queryset().get(level=level)
            serializer = self.get_serializer(content)
            return Response(serializer.data)
        except TopicLevelContent.DoesNotExist:
            return Response({'detail': 'Kontent topilmadi.'}, status=404)


# ─── StudentLevelProgress (Talaba jarayoni) ──────────────────────────────────

class StudentLevelProgressView(generics.GenericAPIView):
    """
    Talabaning mavzu daraja progressini ko'rish va yangilash.
    GET  /topics/{id}/my-progress/
    PATCH /topics/{id}/my-progress/?level=beginner
    """
    permission_classes = [permissions.IsAuthenticated, IsStudentOnly]

    def get(self, request, topic_pk):
        progresses = StudentLevelProgress.objects.filter(
            student=request.user, topic_id=topic_pk
        )
        return Response(StudentLevelProgressSerializer(progresses, many=True).data)

    def patch(self, request, topic_pk):
        """Video ko'rildi / matn o'qildi deb belgilash."""
        level = request.data.get('level') or request.query_params.get('level', 'beginner')

        topic = generics.get_object_or_404(Topic, id=topic_pk)

        # Daraja qulflangan emasligini tekshirish
        if not self._is_level_unlocked(request.user, topic, level):
            return Response(
                {'detail': f"'{level}' daraja hali qulflanmagan. Avvalgi daraja testini o'ting."},
                status=status.HTTP_403_FORBIDDEN
            )

        progress, created = StudentLevelProgress.objects.get_or_create(
            student=request.user,
            topic=topic,
            level=level,
        )

        s = StudentLevelProgressUpdateSerializer(progress, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        progress = s.save()

        # Video + matn o'qilgan bo'lsa — FA ball beriladi
        if progress.video_watched and progress.text_read and not progress.ad_awarded:
            progress.ad_awarded = True
            progress.save(update_fields=['ad_awarded'])

            # TopicScore.fa_score yangilanadi (kontent o'qish uchun)
            self._award_content_score(request.user, topic, level)

        return Response(StudentLevelProgressSerializer(progress).data)

    @staticmethod
    def _is_level_unlocked(user, topic, level):
        if level == 'beginner':
            return True
        try:
            ts = TopicScore.objects.get(student=user, topic=topic)
            if level == 'intermediate':
                return ts.beginner_test_passed
            if level == 'advanced':
                return ts.intermediate_test_passed
        except TopicScore.DoesNotExist:
            return False
        return False

    @staticmethod
    def _award_content_score(user, topic, level):
        """Daraja kontentini o'qib bo'lganda FA ball beradi (+5 har bir daraja uchun)."""
        ts, _ = TopicScore.objects.get_or_create(student=user, topic=topic)
        ts.award_content_read(level)

        # Bildiruv
        try:
            from apps.social.models import Notification
            level_names = {'beginner': "Boshlang'ich", 'intermediate': "O'rta", 'advanced': "Yuqori"}
            Notification.objects.create(
                user=user,
                title=f'{level_names.get(level, level)} daraja kontenti o\'qildi! 📖',
                message=(
                    f'"{topic.title}" mavzusining {level_names.get(level, level)} '
                    f'darajasidagi video va matnni tugatdingiz. '
                    f'+3 FA ball qo\'shildi!'
                ),
                notif_type='topic',
            )
        except Exception:
            pass


# ─── LevelTest ────────────────────────────────────────────────────────────────

class LevelTestViewSet(viewsets.ModelViewSet):
    """Daraja testlari — CRUD faqat o'qituvchilar uchun."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        topic_id = self.kwargs.get('topic_pk')
        return LevelTest.objects.filter(topic_id=topic_id, is_active=True).prefetch_related('questions')

    def get_serializer_class(self):
        if self.request.user.role in ('teacher', 'admin', 'superadmin'):
            return LevelTestTeacherSerializer
        return LevelTestSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'set_questions'):
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        topic_id = self.kwargs.get('topic_pk')
        serializer.save(topic_id=topic_id, created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_test(self, request, topic_pk=None, pk=None):
        """Talaba test javoblarini yuboradi."""
        level_test = self.get_object()

        # Qulflangan testni tekshirish
        if level_test.level != 'beginner':
            topic  = level_test.topic
            locked = True
            try:
                ts = TopicScore.objects.get(student=request.user, topic=topic)
                if level_test.level == 'intermediate':
                    locked = not ts.beginner_test_passed
                elif level_test.level == 'advanced':
                    locked = not ts.intermediate_test_passed
            except TopicScore.DoesNotExist:
                pass
            if locked:
                return Response(
                    {'detail': 'Bu daraja testi hali qulflanmagan.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        s = LevelTestSubmitSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        answers = s.validated_data['answers']   # {str(question_id): option_index}

        # To'g'ri javoblarni hisoblash
        questions = level_test.questions.all()
        score     = 0
        for q in questions:
            selected = answers.get(str(q.id))
            if selected is not None and int(selected) == q.correct_answer:
                score += 1

        passed = score >= level_test.pass_score

        # Urinish raqami
        prev_attempts = StudentLevelTestResult.objects.filter(
            student=request.user, level_test=level_test
        ).count()
        result = StudentLevelTestResult.objects.create(
            student    = request.user,
            level_test = level_test,
            score      = score,
            passed     = passed,
            answers    = {str(k): v for k, v in answers.items()},
            attempt_no = prev_attempts + 1,
        )

        # O'tgan bo'lsa TopicScore yangilanadi
        if passed:
            try:
                ts, _ = TopicScore.objects.get_or_create(
                    student=request.user,
                    topic=level_test.topic,
                )
                ts.award_level_test(level_test.level)

                # Bildiruv
                from apps.social.models import Notification
                level_names = {'beginner': "Boshlang'ich", 'intermediate': "O'rta", 'advanced': "Yuqori"}
                Notification.objects.create(
                    user=request.user,
                    title=f'{level_names.get(level_test.level, "")} daraja testi o\'tdi! ✓',
                    message=(
                        f'{level_test.topic.title} — {score}/10 to\'g\'ri javob. '
                        f'+{LevelTest.KO_SCORE_MAP.get(level_test.level, 0)} KO ball qo\'shildi.'
                    ),
                    notif_type='topic',
                )
            except Exception:
                pass

        return Response({
            'score':      score,
            'total':      questions.count(),
            'passed':     passed,
            'pass_score': level_test.pass_score,
            'attempt_no': result.attempt_no,
            'ko_reward':  LevelTest.KO_SCORE_MAP.get(level_test.level, 0) if passed else 0,
        })

    @action(detail=True, methods=['get'], url_path='my-results')
    def my_results(self, request, topic_pk=None, pk=None):
        """Talabaning test tarixi."""
        level_test = self.get_object()
        results    = StudentLevelTestResult.objects.filter(
            student=request.user, level_test=level_test
        ).order_by('-completed_at')
        return Response(StudentLevelTestResultSerializer(results, many=True).data)

    @action(detail=True, methods=['post'], url_path='set-questions')
    @transaction.atomic
    def set_questions(self, request, topic_pk=None, pk=None):
        """10 ta test savolini to'liq almashtirish (bulk). O'qituvchi uchun."""
        level_test = self.get_object()
        questions_data = request.data.get('questions', [])
        if not isinstance(questions_data, list):
            return Response({'detail': 'questions massiv bo\'lishi kerak.'}, status=400)
        if len(questions_data) > 10:
            return Response({'detail': 'Maksimum 10 ta savol.'}, status=400)

        level_test.questions.all().delete()
        LevelTestQuestion.objects.bulk_create([
            LevelTestQuestion(
                test=level_test,
                question=q.get('question', ''),
                options=q.get('options', []),
                correct_answer=int(q.get('correct_answer', 0)),
                explanation=q.get('explanation', ''),
                order=q.get('order', i),
            )
            for i, q in enumerate(questions_data)
        ])
        level_test.refresh_from_db()
        return Response(LevelTestTeacherSerializer(level_test, context={'request': request}).data)


# ─── TopicScore ───────────────────────────────────────────────────────────────

class TopicScoreViewSet(viewsets.ModelViewSet):
    serializer_class   = TopicScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return TopicScore.objects.filter(student=user).select_related('topic')
        student_id = self.request.query_params.get('student')
        qs = TopicScore.objects.select_related('student', 'topic')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsTeacherOrAdmin],
            url_path='give-mo')
    def give_mo_score(self, request, pk=None):
        """O'qituvchi MO (motivatsion) ballini beradi."""
        score = self.get_object()
        s = TopicScoreTeacherUpdateSerializer(score, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        score.save()

        from apps.social.models import Notification
        Notification.objects.create(
            user=score.student,
            title="O'qituvchi motivatsion ball berdi ⭐",
            message=(
                f'"{score.topic.title}" mavzusi uchun motivatsion ball: '
                f'{score.mo_score}/15 (o\'qituvchi: {request.user.get_full_name()})'
            ),
            notif_type='teacher',
        )
        return Response(TopicScoreSerializer(score).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsTeacherOrAdmin],
            url_path='give-fa-project')
    def give_fa_project(self, request, pk=None):
        """O'qituvchi FA loyiha ballini beradi (max 10)."""
        score = self.get_object()
        s = TopicScoreFaProjectUpdateSerializer(score, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        score.save()

        from apps.social.models import Notification
        Notification.objects.create(
            user=score.student,
            title="Loyiha baholandi 💻",
            message=(
                f'"{score.topic.title}" mavzusi loyihasi uchun ball: '
                f'{score.fa_project_score}/10 · '
                f'Jami FA: {score.fa_score + score.fa_project_score}/30 '
                f'(o\'qituvchi: {request.user.get_full_name()})'
            ),
            notif_type='teacher',
        )
        return Response(TopicScoreSerializer(score).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsTeacherOrAdmin],
            url_path='give-re-peer')
    def give_re_peer(self, request, pk=None):
        """O'qituvchi RE peer-review sifati ballini beradi (max 10)."""
        score = self.get_object()
        s = TopicScoreRePeerUpdateSerializer(score, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        score.save()

        from apps.social.models import Notification
        Notification.objects.create(
            user=score.student,
            title="Peer-review baholandi 🔄",
            message=(
                f'"{score.topic.title}" mavzusi peer-review uchun ball: '
                f'{score.re_peer_score}/10 · '
                f'Jami RE: {score.re_score + score.re_peer_score}/20 '
                f'(o\'qituvchi: {request.user.get_full_name()})'
            ),
            notif_type='teacher',
        )
        return Response(TopicScoreSerializer(score).data)


# ─── Task ────────────────────────────────────────────────────────────────────

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['topic', 'level', 'task_category', 'task_type', 'is_active']

    def get_queryset(self):
        return Task.objects.filter(is_active=True).select_related('topic')

    def get_serializer_class(self):
        if self.request.user.role == 'student':
            return TaskStudentSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]


# ─── Submission ───────────────────────────────────────────────────────────────

class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class   = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['task', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Submission.objects.filter(student=user).select_related('task')
        return Submission.objects.select_related('student', 'task')

    def create(self, request, *args, **kwargs):
        s = SubmissionCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        submission = Submission.objects.create(
            student  = request.user,
            task     = s.validated_data['task'],
            code     = s.validated_data['code'],
            language = s.validated_data.get('language', 'csharp'),
        )
        from .tasks import submit_to_judge0
        submit_to_judge0.delay(submission.id)
        return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)


# ─── DiagnosticTest ───────────────────────────────────────────────────────────

class DiagnosticTestView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            test = DiagnosticTest.objects.get(student=request.user)
            return Response(DiagnosticTestSerializer(test).data)
        except DiagnosticTest.DoesNotExist:
            return Response({'detail': 'Test topilmadi.'}, status=404)

    def post(self, request):
        if DiagnosticTest.objects.filter(student=request.user).exists():
            return Response({'detail': 'Test allaqachon topshirilgan.'}, status=400)

        s = DiagnosticTestSubmitSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        answers      = s.validated_data['answers']
        score, level = calculate_diagnostic_level(answers)

        test = DiagnosticTest.objects.create(
            student=request.user, score=score, level=level, answers=answers
        )

        # Barcha mavzular uchun TopicScore yaratish
        topics = Topic.objects.filter(is_active=True)
        TopicScore.objects.bulk_create([
            TopicScore(student=request.user, topic=t, level=level)
            for t in topics
        ], ignore_conflicts=True)

        return Response(DiagnosticTestSerializer(test).data, status=201)


# ─── AI Teacher Report ───────────────────────────────────────────────────────

class AITeacherReportView(generics.GenericAPIView):
    """
    O'qituvchi uchun AI tahlili.
    GET /api/courses/ai-report/?student_id=X
    GET /api/courses/ai-report/?student_id=X&topic_id=Y
    Faqat teacher/admin uchun.
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        from django.conf import settings
        import openai

        student_id = request.query_params.get('student_id')
        topic_id   = request.query_params.get('topic_id')

        if not student_id:
            return Response({'detail': 'student_id parametri kerak.'}, status=400)

        try:
            from apps.users.models import User, StudentProfile
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response({'detail': 'Talaba topilmadi.'}, status=404)

        # Ma'lumot yig'ish
        try:
            profile = student.student_profile
        except Exception:
            return Response({'detail': 'Talaba profili topilmadi.'}, status=404)

        # Ballar
        scores_qs = TopicScore.objects.filter(student=student).select_related('topic')
        if topic_id:
            scores_qs = scores_qs.filter(topic_id=topic_id)
        scores_qs = scores_qs[:10]  # Max 10 mavzu

        scores_info = []
        for ts in scores_qs:
            fa_total = ts.fa_score + ts.fa_project_score
            re_total = ts.re_score + ts.re_peer_score
            scores_info.append(
                f"- {ts.topic.title}: MO={ts.mo_score}/15, KO={ts.ko_score}/35, "
                f"FA={fa_total}/30 (loyiha:{ts.fa_project_score}), "
                f"RE={re_total}/20 (peer:{ts.re_peer_score}) "
                f"(Jami: {ts.total_score}/100)"
            )

        # Submission statistikasi
        total_sub  = Submission.objects.filter(student=student).count()
        passed_sub = Submission.objects.filter(student=student, status='passed').count()

        # Prompt
        student_name = student.get_full_name() or student.username
        scores_text  = '\n'.join(scores_info) if scores_info else 'Ma\'lumot yo\'q'

        prompt = (
            f"Coders War platformasidagi talaba '{student_name}' haqida o'qituvchiga "
            f"tavsiya va tahlil yozing (o'zbek tilida, 150-200 so'z).\n\n"
            f"Talaba ma'lumotlari:\n"
            f"- Daraja: {profile.level} ({profile.rating_score} ball)\n"
            f"- Streak: {profile.current_streak} kun\n"
            f"- Submission: {passed_sub}/{total_sub} muvaffaqiyatli\n\n"
            f"Mavzular bo'yicha ball:\n{scores_text}\n\n"
            f"Tahlil quyidagilarni o'z ichiga olsin:\n"
            f"1. Talabaning kuchli tomonlari\n"
            f"2. Zaif tomonlar va qanday yaxshilash mumkin\n"
            f"3. Keyingi qadamlar uchun tavsiyalar"
        )

        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key or api_key.startswith('sk-your'):
            # Demo rejim — OpenAI kalit bo'lmasa
            return Response({
                'student':  student_name,
                'level':    profile.level,
                'score':    profile.rating_score,
                'report':   (
                    f"[Demo rejim] '{student_name}' talabasi {profile.level} darajasida "
                    f"{profile.rating_score} ball to'plagan. "
                    f"Streak: {profile.current_streak} kun. "
                    f"Submission: {passed_sub}/{total_sub} muvaffaqiyatli. "
                    f"AI hisoboti uchun OPENAI_API_KEY ni sozlang."
                ),
                'demo':     True,
            })

        try:
            client = openai.OpenAI(api_key=api_key)
            resp   = client.chat.completions.create(
                model    = 'gpt-4o-mini',
                messages = [
                    {'role': 'system', 'content': 'Siz tajribali dasturlash o\'qituvchisisiz. O\'zbek tilida javob bering.'},
                    {'role': 'user',   'content': prompt},
                ],
                max_tokens  = 600,
                temperature = 0.7,
            )
            report_text = resp.choices[0].message.content.strip()
        except Exception as e:
            return Response({'detail': f'AI hisoboti xatosi: {str(e)}'}, status=500)

        return Response({
            'student': student_name,
            'level':   profile.level,
            'score':   profile.rating_score,
            'report':  report_text,
            'demo':    False,
        })


# ─── ReflectionJournal ───────────────────────────────────────────────────────

class ReflectionJournalViewSet(viewsets.ModelViewSet):
    serializer_class   = ReflectionJournalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReflectionJournal.objects.filter(student=self.request.user).select_related('topic')

    def perform_create(self, serializer):
        obj = serializer.save(student=self.request.user)
        self._award_re_score(obj)

    def perform_update(self, serializer):
        serializer.save(student=self.request.user)

    @staticmethod
    def _award_re_score(journal):
        """Refleksiya jurnali yozilganda avtomatik RE ball: max 10 (bir marta to'liq)."""
        try:
            ts = TopicScore.objects.get(student=journal.student, topic=journal.topic)
            if ts.re_score < 10:
                ts.re_score = 10   # O'z-o'zini baholash formasi — to'liq 10 ball
                ts.save(update_fields=['re_score'])
        except TopicScore.DoesNotExist:
            pass
