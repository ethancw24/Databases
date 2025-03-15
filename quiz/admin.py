from django.contrib import admin
from .models import Topic, Question, Answer, QuizProgress

admin.site.register(Topic)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(QuizProgress)
