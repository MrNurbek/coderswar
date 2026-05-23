"""
Celery asinxron vazifalar — Judge0 polling.
"""
import time
from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=15, default_retry_delay=3)
def submit_to_judge0(self, submission_id: int):
    """
    Submissionni Judge0 ga yuboradi va natijani kutadi (polling).
    Har 3 soniyada bir marta tekshiradi, maksimum 15 marta.
    """
    from .models import Submission
    from .services import judge0_submit, judge0_get_result, run_all_test_cases

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
            j0 = judge0_submit(sub.code, tc.get('input', ''), tc.get('output', ''))
            token = j0.get('token')

            # Natijani polling orqali kutish
            for _ in range(10):
                time.sleep(2)
                result = judge0_get_result(token)
                if result.get('status', {}).get('id', 1) > 2:
                    break

            status_id = result.get('status', {}).get('id', 6)  # 6=Error default
            accepted  = (status_id == 3)  # 3 = Accepted

            results.append({
                'input':        tc.get('input', ''),
                'expected':     tc.get('output', ''),
                'actual':       result.get('stdout', '').strip(),
                'status_id':    status_id,
                'status_desc':  result.get('status', {}).get('description', ''),
                'passed':       accepted,
                'runtime_ms':   result.get('time') and int(float(result['time']) * 1000),
                'memory_kb':    result.get('memory'),
            })
            if accepted:
                passed += 1

    except Exception as exc:
        sub.status        = Submission.Status.ERROR
        sub.error_message = str(exc)
        sub.save(update_fields=['status', 'error_message'])
        raise self.retry(exc=exc)

    # Natijalarni yozish
    all_passed = (passed == len(task.test_cases))
    sub.test_results  = results
    sub.status        = Submission.Status.PASSED if all_passed else Submission.Status.FAILED
    sub.score_awarded = task.max_score if all_passed else 0
    if results:
        runtimes = [r['runtime_ms'] for r in results if r.get('runtime_ms')]
        memories = [r['memory_kb'] for r in results if r.get('memory_kb')]
        sub.runtime_ms = max(runtimes) if runtimes else None
        sub.memory_kb  = max(memories) if memories else None

    sub.save(update_fields=['status', 'test_results', 'score_awarded', 'runtime_ms', 'memory_kb'])

    # Fa (faoliyat) ballini yangilash — topshirilgan har bir task uchun
    if all_passed:
        _update_fa_score(sub)
        _drop_equipment(sub)
        # Badge tekshiruvi — submissions, runtime_ms, topics_completed va h.k.
        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(sub.student)
        except Exception:
            pass
        # Duel natijasini WebSocket orqali yuborish (agar duel topshirig'i bo'lsa)
        try:
            from apps.gamification.consumers import notify_duel_result
            notify_duel_result(submission_id)
        except Exception:
            pass


def _update_fa_score(submission):
    """Muvaffaqiyatli submission uchun Fa ballini oshirish."""
    from .models import TopicScore
    try:
        ts = TopicScore.objects.get(
            student=submission.student,
            topic=submission.task.topic,
        )
        new_fa = min(30, ts.fa_score + submission.score_awarded)
        ts.fa_score = new_fa
        ts.attempt_count += 1
        ts.save(update_fields=['fa_score', 'attempt_count'])
    except TopicScore.DoesNotExist:
        pass


def _drop_equipment(submission):
    """Topshiriq o'tganda random qurol/aslaha tushirish va bildiruv yuborish."""
    try:
        from apps.gamification.models import roll_equipment_drop
        from apps.social.models import Notification

        task = submission.task
        ue = roll_equipment_drop(
            user=submission.student,
            task_level=task.level,
            task_category=task.task_category,
        )
        if not ue:
            return

        eq = ue.equipment
        rarity_labels = {
            'common': 'Oddiy', 'rare': 'Noyob',
            'epic': 'Epic',   'legendary': '⭐ Afsonaviy',
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
        pass  # drop xatoligi asosiy jarayonga ta'sir qilmasin
