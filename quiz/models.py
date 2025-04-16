from django.db import models
from django.contrib.auth.models import AbstractUser, User

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    admin_level = models.IntegerField()

    def __str__(self):
        return f"Admin: {self.user.username} (Level {self.admin_level})"

class RegisteredUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    trust_rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"Registered: {self.user.username} (Trust {self.trust_rating})"

class Question(models.Model):
    qnum = models.AutoField(primary_key=True)
    text = models.TextField()
    wrong_answers = models.TextField(help_text="JSON list of wrong answers")
    trust_rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"Q{self.qnum}: {self.text[:50]}..."

class RightAnswer(models.Model):
    qnum = models.OneToOneField(Question, on_delete=models.CASCADE, primary_key=True)
    text = models.TextField()

    def __str__(self):
        return f"Answer for Q{self.qnum.qnum}"
    
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    taken_at = models.DateTimeField(auto_now_add=True)