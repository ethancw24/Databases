# Generated by Django 5.0.6 on 2025-02-18 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_remove_question_correct_answer_answer_is_correct_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='explanation',
        ),
    ]
