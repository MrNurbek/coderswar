# utils/semesters.py  (yangi fayl)
from django.db.models import Case, When, IntegerField, Value

def semester_case_expression():
    return Case(
        When(topic__order__gte=1,  topic__order__lte=15, then=Value(1)),
        When(topic__order__gte=16, topic__order__lte=26, then=Value(2)),
        When(topic__order__gte=27, topic__order__lte=45, then=Value(3)),
        default=Value(0),
        output_field=IntegerField(),
    )
