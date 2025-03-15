# quiz/models.py
from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

class Answer(models.Model):
    text = models.CharField(max_length=200)
    #explanation = models.TextField()  # Explanation for why this answer is correct/incorrect
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)  # Mark if this is the correct answer

    def __str__(self):
        return self.text


class QuizProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    quiz_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.score} - {self.quiz_date}'
