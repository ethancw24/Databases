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
    path('delete-question/<int:qnum>/', views.delete_question, name='delete_question'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete-all-questions/', views.delete_all_questions, name='delete_all_questions'),
    path('generate-questions/', views.generate_questions, name='generate_questions'),
]