from apps.initialtest.models import InitialTest, InitialTestAnswer
from rest_framework import serializers



class InitialTestAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialTestAnswer
        fields = ['id', 'answer_text']

class InitialTestSerializer(serializers.ModelSerializer):
    answers = InitialTestAnswerSerializer(many=True)

    class Meta:
        model = InitialTest
        fields = ['id', 'question', 'order', 'answers']

class InitialTestSubmitSerializer(serializers.Serializer):
    answers = serializers.ListField(
        help_text="Tanlangan javoblar ro‘yxati, har bir elementda javob ID si bo‘ladi",
        child=serializers.DictField(
            child=serializers.IntegerField(help_text="Variant ID si (InitialTestAnswer.id)")
        )
    )
