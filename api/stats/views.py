# api/stats/views.py yoki apps/stats/views.py (qayerga qo‘ygan bo‘lsangiz)
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django import forms
from .services import semester_points_global, semester_topic_counts, per_user_semester_points, MAX_POINTS

class StatsFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Qidiruv (email/ism)")
    otm = forms.CharField(required=False, label="OTM")
    course = forms.IntegerField(required=False, label="Kurs")
    group = forms.CharField(required=False, label="Guruh")
    role = forms.ChoiceField(
        required=False, label="Rol",
        choices=[('', '---'), ('talaba', 'Talaba'), ('oqituvchi', 'O‘qituvchi')]
    )

@staff_member_required
def admin_stats_view(request):
    # Umumiy semestr kartalari + bar chart
    sem = semester_points_global()
    counts = semester_topic_counts()

    cards = [
        {"title": "1-semestr ball", "value": f"{sem[1]['points']} / {sem[1]['max_points']}", "pct": sem[1]['progress_pct']},
        {"title": "2-semestr ball", "value": f"{sem[2]['points']} / {sem[2]['max_points']}", "pct": sem[2]['progress_pct']},
        {"title": "3-semestr ball", "value": f"{sem[3]['points']} / {sem[3]['max_points']}", "pct": sem[3]['progress_pct']},
    ]
    series = [
        {"label": "1-semestr", "value": sem[1]['points']},
        {"label": "2-semestr", "value": sem[2]['points']},
        {"label": "3-semestr", "value": sem[3]['points']},
    ]
    summary_table = {
        "title": "Semestr bo‘yicha umumiy statistika",
        "headers": ["Semestr", "Topics", "Yakunlar (count)", "Ball (sum)", "Max", "Progress %"],
        "rows": [
            ["1", counts[1], sem[1]['completed'], sem[1]['points'], sem[1]['max_points'], f"{sem[1]['progress_pct']}%"],
            ["2", counts[2], sem[2]['completed'], sem[2]['points'], sem[2]['max_points'], f"{sem[2]['progress_pct']}%"],
            ["3", counts[3], sem[3]['completed'], sem[3]['points'], sem[3]['max_points'], f"{sem[3]['progress_pct']}%"],
        ]
    }

    # Filtrlar
    form = StatsFilterForm(request.GET or None)
    filters = {}
    if form.is_valid():
        filters = {k: v for k, v in form.cleaned_data.items() if v not in (None, '', [])}

    # Har bir foydalanuvchi bo‘yicha semestr ballari
    user_rows = per_user_semester_points(filters=filters)

    # User jadval: barcha foydalanuvchilarning 1/2/3 sem ballari + jami
    user_table = {
        "title": "Foydalanuvchilar kesimida semestr ballari",
        "headers": [
            "F.I.Sh / Email", "Reyting",
            f"1-sem ({MAX_POINTS[1]} max)", f"2-sem ({MAX_POINTS[2]} max)", f"3-sem ({MAX_POINTS[3]} max)",
            "Jami"
        ],
        "rows": [
            [
                f"{r['name']} ({r['email']})",
                r['rating'],
                f"{r['sem1_points']}  ({r['sem1_pct']}%)",
                f"{r['sem2_points']}  ({r['sem2_pct']}%)",
                f"{r['sem3_points']}  ({r['sem3_pct']}%)",
                r['total_points'],
            ]
            for r in user_rows
        ]
    }

    tables = [summary_table, user_table]

    return render(
        request,
        "admin/stats.html",
        {
            "cards": cards,
            "series": series,
            "tables": tables,
            "filter_form": form,
        },
    )
