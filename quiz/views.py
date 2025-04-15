from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from quiz.models import Question
from.generate_question import save_to_db
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

@staff_member_required
def manage_questions(request):
    questions = Question.objects.all()
    return render(request, 'quiz/manage_questions.html', {'questions': questions})

@staff_member_required
@require_POST
def delete_question(request, qnum):
    Question.objects.filter(qnum=qnum).delete()
    return redirect('quiz:manage_questions')

@staff_member_required
@require_POST
def delete_all_questions(request):
    Question.objects.all().delete()
    return redirect('quiz:manage_questions')

@staff_member_required
@require_POST
def generate_questions(request):
    count = 0
    for _ in range(10):
        if save_to_db():
            count += 1
    return redirect('quiz:manage_questions')

@login_required
def start_quiz(request):
    questions = list(Question.objects.all())
    random.shuffle(questions)
    selected_questions = questions[:8]
    for q in selected_questions:
        q.wrong_list = q.wrong_answers.split(",")
    return render(request, 'quiz/quiz.html', {'questions': selected_questions})

@login_required
def submit_quiz(request):
    if request.method == 'POST':
        from .generate_question import save_to_db  # Import the generator
        questions = Question.objects.all()
        score = 0
        explanations = []

        for question in questions:
            selected = request.POST.get(f"question_{question.qnum}")
            correct = RightAnswer.objects.get(qnum=question).text
            is_correct = selected == correct
            if is_correct:
                score += 1
                # Trust bumps up toward 1.0
                question.trust_rating = (question.trust_rating + 1.0) / 2
            else:
                # Trust drops toward 0
                question.trust_rating = (question.trust_rating + 0.0) / 2

            question.save()
            explanations.append((question.text, selected, correct))

            if question.trust_rating < 0.6:
                question.delete()  # Will cascade and remove RightAnswer too
                save_to_db()       # Replace with a new question

        return render(request, 'quiz/result.html', {
            'score': score,
            'total': len(questions),
            'explanations': explanations
        })

    return redirect('quiz:home')

