from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import Question, Topic, QuizProgress
from django.contrib.auth.decorators import login_required
import random

# Home page view
def home(request):
    topics = Topic.objects.all()  # Display available topics on the home page
    return render(request, 'quiz/home.html', {'topics': topics})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('quiz:home')
    else:
        form = AuthenticationForm()
    return render(request, 'quiz/login.html', {'form': form})

# Register view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('quiz:home')
    else:
        form = RegisterForm()
    return render(request, 'quiz/register.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('quiz:home')

# Start quiz view (requires user to be logged in)
@login_required
def start_quiz(request, topic_id):
    # Get questions for the selected topic
    topic = Topic.objects.get(id=topic_id)
    questions = list(Question.objects.filter(topic=topic))
    random.shuffle(questions)  # Shuffle questions
    selected_questions = questions[:8]  # Select 8 random questions
    return render(request, 'quiz/quiz.html', {'questions': selected_questions, 'topic': topic})

# Submit quiz answers and calculate the score
@login_required
def submit_quiz(request, topic_id):
    if request.method == 'POST':
        topic = Topic.objects.get(id=topic_id)
        questions = Question.objects.filter(topic=topic)
        score = 0
        explanations = []

        for question in questions:
            selected_answer_id = request.POST.get(f"question_{question.id}")
            if selected_answer_id:
                selected_answer = Question.objects.get(id=selected_answer_id)
                if selected_answer == question.correct_answer:
                    score += 1
                explanations.append((question.text, selected_answer.text, selected_answer.explanation))

        # Save quiz progress
        QuizProgress.objects.create(user=request.user, score=score)

        return render(request, 'quiz/result.html', {
            'score': score,
            'total': len(questions),
            'explanations': explanations
        })

    return redirect('quiz:home')
