from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import RegisterForm
from .models import Question, RightAnswer, User
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render
from quiz.models import Question
from .generate_question import save_to_db
from django.db.models import Avg
from .models import QuizAttempt
import random
import json

@login_required
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
def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})

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

@staff_member_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    if not user.is_staff:  # Don't delete admin accounts
        user.delete()
    return redirect('quiz:manage_users')

@login_required
def start_quiz(request):
    questions = list(Question.objects.all())
    random.shuffle(questions)
    selected_questions = questions[:8]

    for q in selected_questions:
        try:
            wrongs = json.loads(q.wrong_answers)
            wrongs = [ans.strip().strip("[]\"'") for ans in wrongs][:3]
        except Exception as e:
            print(f"Failed to parse wrong_answers for Q{q.qnum}: {e}")
            wrongs = []

        try:
            correct = q.rightanswer.text.strip().strip("[]\"'")
        except Exception as e:
            print(f"Failed to parse correct_answers for Q{q.qnum}: {e}")
            correct = ""

        # Combine all answers and shuffle
        options = wrongs + [correct]
        random.shuffle(options)

        # Attach all of the possible answers to the question list
        q.option_list = options

    # Save selected question IDs in session
    request.session['quiz_qnums'] = [q.qnum for q in selected_questions]

    return render(request, 'quiz/quiz.html', {'questions': selected_questions})

@login_required
def submit_quiz(request):
    if request.method == 'POST':
        quiz_qnums = request.session.get('quiz_qnums', [])
        questions = Question.objects.filter(qnum__in=quiz_qnums)
        score = 0
        results = []

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
            
            # Question result information
            results.append({
                'text': question.text,
                'selected': selected,
                'correct': correct,
                'is_correct': is_correct,
                'explanation': generate_explanation(question.text, correct)
            })

            if question.trust_rating < 0.6:
                question.delete()  # Will cascade and remove RightAnswer too
                save_to_db()       # Replace with a new question

        QuizAttempt.objects.create(user=request.user, score=score, total=len(questions))
        avg = QuizAttempt.objects.filter(user=request.user).aggreagate(avg_score=Avg('score'))['avg']

        return render(request, 'quiz/result.html', {
            'score': score,
            'total': len(questions),
            'explanations': explanations,
            'avg': avg
        })

    return redirect('quiz:home')

# IF TIME PERMITS, HAVE THE AI EXPLAIN WHY AN ANSWER IS CORRECT
def generate_explanation(question, correct_answer):
    return f"The correct answer {correct_answer} is based off of Python"