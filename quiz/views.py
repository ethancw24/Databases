from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
#from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
#from django.http import HttpResponseRedirect
#from django.urls import reverse
from .forms import RegisterForm, LoginForm
from .generate_question import save_to_db
from django.views.decorators.http import require_POST
from django.db import connection
import random
import json

@login_required
def home(request):
    return render(request, 'quiz/home.html')

def auth_view(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('quiz:home')
        else:
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('quiz:home')

    return render(request, 'quiz/auth.html', {
        'login_form': login_form,
        'register_form': register_form
    })

def logout_view(request):
    logout(request)
    return redirect('quiz:home')

@staff_member_required
def manage_questions(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT qnum, text FROM quiz_question")
        questions = [{'qnum': row[0], 'text': row[1]} for row in cursor.fetchall()]
    return render(request, 'quiz/manage_questions.html', {'questions': questions})

@staff_member_required
def manage_users(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, email, is_staff FROM quiz_user")
        users = [{'id': row[0], 'username': row[1], 'email': row[2], 'is_staff': row[3]} for row in cursor.fetchall()]
    return render(request, 'quiz/manage_users.html', {'users': users})

@require_POST
def delete_question(request, qnum):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM quiz_rightanswer WHERE qnum_id = %s", [qnum])
        cursor.execute("DELETE FROM quiz_question WHERE qnum = %s", [qnum])
    return redirect('quiz:manage_questions')

@staff_member_required
@require_POST
def delete_all_questions(request):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM quiz_rightanswer")
        cursor.execute("DELETE FROM quiz_question")
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
    with connection.cursor() as cursor:
        cursor.execute("SELECT is_staff FROM quiz_user WHERE id = %s", [user_id])
        result = cursor.fetchone()
        if result and not result[0]:
            cursor.execute("DELETE FROM quiz_user WHERE id = %s", [user_id])
    return redirect('quiz:manage_users')

@login_required
def start_quiz(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT qnum, text, wrong_answers FROM quiz_question")
        all_questions = cursor.fetchall()
    random.shuffle(all_questions)
    selected_questions = all_questions[:8]
    quiz_questions = []

    for row in selected_questions:
        qnum, text, wrong_answers_json = row
        try:
            wrongs = json.loads(wrong_answers_json)
            wrongs = [ans.strip().strip("[]\"'") for ans in wrongs][:3]
        except:
            wrongs = []

        with connection.cursor() as cursor:
            cursor.execute("SELECT text FROM quiz_rightanswer WHERE qnum_id = %s", [qnum])
            right_row = cursor.fetchone()
        correct = right_row[0].strip().strip("[]\"'") if right_row else ""

        options = wrongs + [correct]
        random.shuffle(options)

        quiz_questions.append({
            'qnum': qnum,
            'text': text,
            'option_list': options
        })

    request.session['quiz_qnums'] = [q['qnum'] for q in quiz_questions]
    return render(request, 'quiz/quiz.html', {'questions': quiz_questions})

@login_required
def submit_quiz(request):
    if request.method == 'POST':
        quiz_qnums = request.session.get('quiz_qnums', [])
        score = 0
        results = []

        with connection.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(quiz_qnums))
            cursor.execute(f"SELECT qnum, text, trust_rating, wrong_answers FROM quiz_question WHERE qnum IN ({format_strings})", quiz_qnums)
            questions = cursor.fetchall()

        for qnum, text, trust_rating, _ in questions:
            selected = request.POST.get(f"question_{qnum}")

            with connection.cursor() as cursor:
                cursor.execute("SELECT text FROM quiz_rightanswer WHERE qnum_id = %s", [qnum])
                right_row = cursor.fetchone()

            correct = right_row[0] if right_row else ""
            is_correct = selected == correct

            new_trust = (trust_rating + (1.0 if is_correct else 0.0)) / 2

            with connection.cursor() as cursor:
                cursor.execute("UPDATE quiz_question SET trust_rating = %s WHERE qnum = %s", [new_trust, qnum])

            results.append({
                'text': text,
                'selected': selected,
                'correct': correct,
                'is_correct': is_correct,
                'explanation': generate_explanation(text, correct)
            })

            if new_trust < 0.6:
                delete_question(request, qnum)
                save_to_db()

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO quiz_quizattempt (user_id, score, total, taken_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)", [request.user.id, score, len(questions)])
            cursor.execute("SELECT AVG(score) FROM quiz_quizattempt WHERE user_id = %s", [request.user.id])
            avg = cursor.fetchone()[0]

        return render(request, 'quiz/result.html', {
            'score': score,
            'total': len(questions),
            'explanations': results,
            'avg': avg
        })

    return redirect('quiz:home')

# IF TIME PERMITS, HAVE THE AI EXPLAIN WHY AN ANSWER IS CORRECT
def generate_explanation(question, correct_answer):
    return f"The correct answer {correct_answer} is based off of Python"