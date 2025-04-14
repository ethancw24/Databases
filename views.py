from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import Question, RightAnswer
import random

def home(request):
    return render(request, 'quiz/home.html')

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

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('quiz:home')
    else:
        form = RegisterForm()
    return render(request, 'quiz/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('quiz:home')

@login_required
def start_quiz(request):
    questions = list(Question.objects.all())
    random.shuffle(questions)
    selected_questions = questions[:8]
    return render(request, 'quiz/quiz.html', {'questions': selected_questions})

@login_required
def submit_quiz(request):
    if request.method == 'POST':
        questions = Question.objects.all()
        score = 0
        explanations = []

        for question in questions:
            selected = request.POST.get(f"question_{question.qnum}")
            correct = RightAnswer.objects.get(qnum=question).text
            is_correct = selected == correct
            if is_correct:
                score += 1
            explanations.append((question.text, selected, correct))

        return render(request, 'quiz/result.html', {
            'score': score,
            'total': len(questions),
            'explanations': explanations
        })

    return redirect('quiz:home')
