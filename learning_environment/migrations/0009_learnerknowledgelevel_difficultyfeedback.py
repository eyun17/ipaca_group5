# Generated by Django 4.1.3 on 2022-11-25 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("learning_environment", "0008_taskdifficulty"),
    ]

    operations = [
        migrations.CreateModel(
            name="LearnerKnowledgeLevel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                (
                    "level",
                    models.IntegerField(
                        choices=[
                            (1, "Easy"),
                            (2, "Beginner"),
                            (3, "Intermediate"),
                            (4, "Advanced"),
                            (5, "Mastery"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning_environment.lesson",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DifficultyFeedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("knowledge", models.IntegerField(default=0)),
                ("redo_count", models.IntegerField(default=0)),
                ("ita_feedback", models.IntegerField(default=1)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="learning_environment.task",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
