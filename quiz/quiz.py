from django.shortcuts import render, redirect
from .models import Question, Answer, QuizProgress, Topic
from django.contrib.auth.decorators import login_required

def home(request):
    topics = Topic.objects.all()
    return render(request, 'quiz/home.html', {'topics': topics})

def start_quiz(request, topic_id):
    questions = Question.objects.filter(topic_id=topic_id).order_by('?')  # Randomize questions
    return render(request, 'quiz/quiz.html', {'questions': questions, 'topic_id': topic_id})

# submit answers
@login_required
def submit_answer(request, question_id):
    question = Question.objects.get(id=question_id)
    selected_answer_id = request.POST.get('answer')
    selected_answer = Answer.objects.get(id=selected_answer_id)
    is_correct = selected_answer == question.correct_answer

    explanation = selected_answer.explanation
    score = 0
    if is_correct:
        score = 1  # Increment score if correct

    # Store progress if needed
    quiz_progress = QuizProgress.objects.create(user=request.user, score=score)

    return render(request, 'quiz/answer.html', {
        'is_correct': is_correct,
        'explanation': explanation,
        'score': score,
        'question': question
    })

# Show final score
def final_score(request):
    # Calculate and display final score
    score = QuizProgress.objects.filter(user=request.user).last().score
    return render(request, 'quiz/final_score.html', {'score': score})
