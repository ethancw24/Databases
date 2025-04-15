from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/submit/', views.submit_quiz, name='submit_quiz'),
    path('manage-questions/', views.manage_questions, name='manage_questions'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-question/<int:qnum>/', views.delete_question, name='delete_question'),
]