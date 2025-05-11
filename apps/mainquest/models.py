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

    def __str__(self):
        return f"CodeExample for {self.plan.title}"


class Assignment(models.Model):
    plan = models.ForeignKey(Plan, related_name='assignments', on_delete=models.CASCADE)
    task_description = models.TextField()
    sample_solution = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Assignment for {self.plan.title}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'topic')
    def __str__(self):
        return self.user.email + "---" + self.topic.title