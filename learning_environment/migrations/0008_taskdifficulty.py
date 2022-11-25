# Generated by Django 4.1.3 on 2022-11-17 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning_environment', '0007_lesson_start_lesson_wrapup'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskDifficulty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (3, 'Hard'), (4, 'Master')])),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_environment.task')),
            ],
        ),
    ]
