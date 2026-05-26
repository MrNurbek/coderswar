"""
Judge0 code evaluation — Redis/Celery siz, threading orqali asinxron.
"""
import time
import threading


# ─── Public API ───────────────────────────────────────────────────────────────

def submit_to_judge0_async(submission_id: int):
    """
    Submissionni Judge0 ga background thread orqali yuboradi.
    Celery .delay() ga to'liq mos keluvchi interfeys.
    """
    t = threading.Thread(
        target=_judge0_worker,
        args=(submission_id,),
        daemon=True,
        name=f'judge0-{submission_id}',
    )
    t.start()


# ─── Worker ───────────────────────────────────────────────────────────────────

def _judge0_worker(submission_id: int):
    """Judge0 API ga kod yuborish, polling va natijani DB ga yozish."""
    from .models import Submission
    from .services import judge0_submit, judge0_get_result

    try:
        sub = Submission.objects.select_related('task').get(id=submission_id)
    except Submission.DoesNotExist:
        return

    sub.status = Submission.Status.RUNNING
    sub.save(update_fields=['status'])

    task    = sub.task
    results = []
    passed  = 0

    try:
        for tc in task.test_cases:
            j0    = judge0_submit(sub.code, tc.get('input', ''), tc.get('output', ''))
            token = j0.get('token')

            # Natijani polling orqali kutish (maks 20 son × 2 sek = 40 sek)
            result = {}
            for _ in range(20):
                time.sleep(2)
                result = judge0_get_result(token)
                if result.get('status', {}).get('id', 1) > 2:
                    break

            status_id = result.get('status', {}).get('id', 6)  # 6 = Error (default)
            accepted  = (status_id == 3)                        # 3 = Accepted

            results.append({
                'input':       tc.get('input', ''),
                'expected':    tc.get('output', ''),
                'actual':      result.get('stdout', '').strip(),
                'status_id':   status_id,
                'status_desc': result.get('status', {}).get('description', ''),
                'passed':      accepted,
                'runtime_ms':  result.get('time') and int(float(result['time']) * 1000),
                'memory_kb':   result.get('memory'),
            })
            if accepted:
                passed += 1

    except Exception as exc:
        sub.status        = Submission.Status.ERROR
        sub.error_message = str(exc)
        sub.save(update_fields=['status', 'error_message'])
        return

    # ── Natijalarni saqlash ──────────────────────────────────────
    all_passed = (passed == len(task.test_cases))

    sub.test_results  = results
    sub.status        = Submission.Status.PASSED if all_passed else Submission.Status.FAILED
    sub.score_awarded = task.max_score if all_passed else 0

    if results:
        runtimes = [r['runtime_ms'] for r in results if r.get('runtime_ms')]
        memories = [r['memory_kb']  for r in results if r.get('memory_kb')]
        sub.runtime_ms = max(runtimes) if runtimes else None
        sub.memory_kb  = max(memories) if memories else None

    sub.save(update_fields=['status', 'test_results', 'score_awarded', 'runtime_ms', 'memory_kb'])

    # ── Post-processing ──────────────────────────────────────────
    if all_passed:
        _update_fa_score(sub)
        _drop_equipment(sub)

        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(sub.student)
        except Exception:
            pass

        try:
            from apps.gamification.consumers import notify_duel_result
            notify_duel_result(submission_id)
        except Exception:
            pass


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _update_fa_score(submission):
    """
    Muvaffaqiyatli submission uchun TopicScore ni yangilash.
    Per-level FA cap va global cap model metodida boshqariladi.
    """
    from .models import TopicScore
    try:
        ts, _ = TopicScore.objects.get_or_create(
            student=submission.student,
            topic=submission.task.topic,
        )
        ts.attempt_count += 1
        ts.save(update_fields=['attempt_count'])

        # exercise → FA ball (per-level cap + global cap ichida)
        # project  → o'qituvchi baholaydi, avtomatik ball berilmaydi
        ts.award_task_score(
            level=submission.task.level,
            category=submission.task.task_category,
        )

        # Bildiruv — faqat exercise uchun
        if submission.task.task_category == 'exercise' and ts.fa_score > 0:
            _notify_exercise_passed(submission, ts)

    except Exception:
        pass


def _notify_exercise_passed(submission, ts):
    """Exercise o'tganda talabaga bildiruv yuborish."""
    try:
        from apps.social.models import Notification
        level_names = {
            'beginner':     "Boshlang'ich",
            'intermediate': "O'rta",
            'advanced':     "Yuqori",
        }
        lvl = level_names.get(submission.task.level, submission.task.level)
        fa_total = ts.fa_score + ts.fa_project_score
        Notification.objects.create(
            user=submission.student,
            title=f'Topshiriq bajarildi! ✅',
            message=(
                f'"{submission.task.title}" ({lvl} daraja) topshirig\'i muvaffaqiyatli bajarildi. '
                f'FA: {fa_total}/30'
            ),
            notif_type='topic',
        )
    except Exception:
        pass


def _drop_equipment(submission):
    """Topshiriq o'tganda random qurol/aslaha tushirish va bildiruv yuborish."""
    try:
        from apps.gamification.models import roll_equipment_drop
        from apps.social.models import Notification

        task = submission.task
        ue   = roll_equipment_drop(
            user=submission.student,
            task_level=task.level,
            task_category=task.task_category,
        )
        if not ue:
            return

        eq = ue.equipment
        rarity_labels = {
            'common': 'Oddiy', 'rare': 'Noyob',
            'epic': 'Epic',    'legendary': '⭐ Afsonaviy',
        }
        bonus_str = ''
        if eq.attack_bonus:  bonus_str += f'+{eq.attack_bonus}% hujum '
        if eq.defense_bonus: bonus_str += f'+{eq.defense_bonus}% himoya'

        Notification.objects.create(
            user=submission.student,
            title=f'{eq.icon} Yangi qurol-aslaha topildi!',
            message=(
                f'"{task.title}" topshirig\'ini bajarib '
                f'{rarity_labels.get(eq.rarity, eq.rarity)} darajali '
                f'{eq.icon} {eq.name} qo\'lga kiritdingiz! '
                f'{bonus_str.strip()} — Profil → Inventarda ko\'ring.'
            ),
            notif_type='badge',
            link='/profile.html',
        )
    except Exception:
        pass
