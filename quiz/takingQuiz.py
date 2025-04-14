# quiz/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from quiz.models import Question, RightAnswer
from quiz.generate_question import save_to_db
import random
import json

@login_required
def home(request):
    return render(request, 'quiz/home.html')

@login_required
@login_required
def start_quiz(request):
    questions = list(Question.objects.all())
    random.shuffle(questions)
    selected_questions = questions[:8] 

    for q in selected_questions:
        try:
            q.wrong_list = json.loads(q.wrong_answers)
        except Exception as e:
            print(f"❌ Failed to parse wrong_answers for Q{q.qnum}: {e}")
            q.wrong_list = []

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
                question.trust_rating = (question.trust_rating + 1.0) / 2
            else:
                question.trust_rating = (question.trust_rating + 0.0) / 2

            question.save()
            explanations.append((question.text, selected, correct))

            if question.trust_rating < 0.6:
                question.delete()
                save_to_db()

        return render(request, 'quiz/result.html', {
            'score': score,
            'total': len(questions),
            'explanations': explanations
        })

    return redirect('quiz:home')
