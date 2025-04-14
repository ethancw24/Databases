from django.contrib import admin
from .models import User, Admin, RegisteredUser, Question, RightAnswer

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'created_at']

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'admin_level']

@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'trust_rating']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['qnum', 'text', 'trust_rating']
    search_fields = ['text']

@admin.register(RightAnswer)
class RightAnswerAdmin(admin.ModelAdmin):
    list_display = ['qnum', 'text']