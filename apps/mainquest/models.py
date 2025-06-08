from django.db import models
from apps.userapp.models import User


class Topic(models.Model):
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Plan(models.Model):
    topic = models.ForeignKey(Topic, related_name='plans', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title


class CodeExample(models.Model):
    plan = models.ForeignKey(Plan, related_name='code_examples', on_delete=models.CASCADE)
    code = models.TextField()
    result = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"CodeExample for {self.plan.title}"


class Assignment(models.Model):
    plan = models.ForeignKey(Plan, related_name='assignments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, help_text="Masalaning sarlavhasi", null=True, blank=True)
    task_description = models.TextField(help_text="Masalaning tavsifi", null=True, blank=True)
    sample_input = models.TextField(help_text="Kiruvchi ma'lumot (stdin)", null=True, blank=True)
    expected_output = models.TextField(help_text="Kutilayotgan chiqish (stdout)", null=True, blank=True)
    order = models.PositiveIntegerField(default=1, help_text="Mavzu ichidagi tartib raqami")
    points = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.title} (Plan: {self.plan.title})"


class AssignmentStatus(models.Model):
    user = models.ForeignKey('userapp.User', on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    earned_points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'assignment')

    def __str__(self):
        return f"{self.user.email} - {self.assignment.title} - {'✔' if self.is_completed else '✘'}"




class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.email} - {self.topic.title}"


class TestCase(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='test_cases', on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return self.assignment.title
