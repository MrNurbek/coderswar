from django.db import models


class InitialTest(models.Model):
    question = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"Initial Test {self.order}"

class InitialTestAnswer(models.Model):
    test = models.ForeignKey(InitialTest, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to Test {self.test.order}: {self.answer_text}"