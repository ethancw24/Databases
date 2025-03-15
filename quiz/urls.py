from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quiz/<int:topic_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:topic_id>/submit/', views.submit_quiz, name='submit_quiz'),
]
