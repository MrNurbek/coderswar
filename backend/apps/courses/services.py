"""
Tashqi servislar bilan ishlash:
- Judge0 API (kod baholash)
- Diagnostik test hisoblash
"""
import requests
from django.conf import settings


# ─── Judge0 ──────────────────────────────────────────────────────────────────

JUDGE0_URL     = getattr(settings, 'JUDGE0_URL', 'http://localhost:2358')
JUDGE0_HEADERS = {'Content-Type': 'application/json'}


def judge0_submit(code: str, stdin: str = '', expected_output: str = '') -> dict:
    """
    Judge0 ga bitta test case yuborish.
    Qaytaradi: {'token': '...', 'status': {...}, ...}
    """
    payload = {
        'language_id':      51,          # C#
        'source_code':      code,
        'stdin':            stdin,
        'expected_output':  expected_output,
        'cpu_time_limit':   2,
        'memory_limit':     262144,      # 256 MB
    }
    resp = requests.post(
        f'{JUDGE0_URL}/submissions?base64_encoded=false&wait=false',
        json=payload,
        headers=JUDGE0_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def judge0_get_result(token: str) -> dict:
    """Token orqali natijani olish."""
    resp = requests.get(
        f'{JUDGE0_URL}/submissions/{token}?base64_encoded=false',
        headers=JUDGE0_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def run_all_test_cases(code: str, test_cases: list) -> list:
    """
    Barcha test case'larni yuborib, natijalarni qaytaradi.
    test_cases: [{'input': '...', 'output': '...'}]
    """
    results = []
    for tc in test_cases:
        try:
            submission = judge0_submit(code, tc.get('input', ''), tc.get('output', ''))
            results.append({
                'token':    submission.get('token'),
                'input':    tc.get('input', ''),
                'expected': tc.get('output', ''),
                'status':   'pending',
            })
        except Exception as e:
            results.append({
                'token':    None,
                'input':    tc.get('input', ''),
                'expected': tc.get('output', ''),
                'status':   'error',
                'message':  str(e),
            })
    return results


# ─── Diagnostik test ─────────────────────────────────────────────────────────

# To'g'ri javoblar (question_id 1-20 -> to'g'ri variant indeksi 0-based)
# Frontend diagnostic.html savollariga mos (QUESTIONS[i].answer, i+1 = question_id)
CORRECT_ANSWERS = {
    '1':  0,   # Microsoft
    '2':  0,   # int x = 5;
    '3':  1,   # 10 % 3 = 1
    '4':  0,   # str1 + str2
    '5':  0,   # do...while kamida bir marta
    '6':  0,   # int[] arr = new int[5];
    '7':  0,   # void — hech narsa qaytarmaydi
    '8':  0,   # Ma'lumotlarni yashirish
    '9':  0,   # Ob'ekt mavjud emasligi
    '10': 0,   # Ha, 2 chiqaradi
    '11': 0,   # Tsikldan chiqish uchun
    '12': 0,   # Interface faqat metod imzolarini
    '13': 0,   # O(n²)
    '14': 0,   # Xatolarni ushlash
    '15': 0,   # Sinf nusxasisiz to'g'ridan-to'g'ri
    '16': 0,   # s.Length = 5
    '17': 0,   # Rekursiyani to'xtatuvchi shart
    '18': 0,   # Ma'lumotlar to'plamini so'rov qilish
    '19': 0,   # O(n log n)
    '20': 0,   # Asinxron operatsiyalarni boshqarish
}


def calculate_diagnostic_level(answers: dict) -> tuple[int, str]:
    """
    Javoblarni baholaydi va darajani aniqlaydi.
    Qaytaradi: (score, level_str)
    score: 0-20, level: 'beginner'|'intermediate'|'advanced'
    """
    score = sum(
        1 for q_id, ans in answers.items()
        if str(CORRECT_ANSWERS.get(str(q_id))) == str(ans)
    )
    score = min(score, 20)

    if score <= 6:
        level = 'beginner'
    elif score <= 13:
        level = 'intermediate'
    else:
        level = 'advanced'

    return score, level
