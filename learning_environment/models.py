from django.db import models
from django.contrib.auth.models import AbstractUser
from learning_environment.its.base import Json5ParseException
from learning_environment.its.tasks import TaskTypeFactory
#from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import json5
import random
import numpy as np
import pandas as pd


class User(AbstractUser):
    """
    This User is used to possibly change the authentication down the line
    """
    pass


class Profile(models.Model):
    """A profile extends the djanog user class with additional fields, like a nickname"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(default="Llama", max_length=64)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile if a user is created"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save the profile if the user data is saved"""
    instance.profile.save()


class ProfileSeriesLevel(models.Model):
    """A user's level within a series"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.CharField(max_length=256, default='General')
    level = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'series')  # ensure there's only one level per user per series



class Lesson(models.Model): # is checked when running read_lessons and then created there
    """
    A selected collection of task
    Comes which has a paragraph

    name: unique identifier
    paragraph: piece of written academic text to read
    tasks: tasks belonging to the lesson
    """
    # TODO: somehow add domain model to lesson

    name = models.CharField(max_length=255)
    lesson_id = models.SlugField(max_length=64)
    series = models.CharField(max_length=255, default='General')
    author = models.CharField(max_length=256)
    text = models.TextField()
    text_source = models.CharField(max_length=1024, null=True)
    text_licence = models.CharField(max_length=1024, null=True)
    text_url = models.URLField(null=True)
    start = models.TextField(null=True)  # text to be displayed before the lesson starts
    wrapup = models.TextField(null=True)  # text to be displyed after the lesson has been finished
    json5 = models.TextField(null=True)

    @classmethod
    def check_json5(cls, lesson_json5):
        """Check if a JSON5 representation of a lesson is valid."""
        try:
            lesson = json5.loads(lesson_json5)
        except ValueError as err:
            raise Json5ParseException("Error in JSON5 code Error message: '{}'".format(err))

        if not isinstance(lesson, dict):
            raise Json5ParseException("Lesson code must be a dictionary.")

        # Checks
        # Mandatory fields
        for lesson_field in ["name", "id", "text", "text_source", "text_licence", "text_url", "author", "tasks"]:
            if lesson_field not in lesson:
                raise Json5ParseException('Field "{}" is missing'.format(lesson_field))
            if not lesson[lesson_field]:
                raise Json5ParseException('Field "{}" is empty'.format(lesson_field))

        # Optional fields must not be empty
        for lesson_field in ['series', 'start', 'wrapup']:
            if lesson_field in lesson and not lesson[lesson_field]:
                raise Json5ParseException('Field "{}" is empty'.format(lesson_field))

        task_num = 0
        for t in lesson["tasks"]:
            task_num += 1
            Task.check_json5(t, task_num)
            
        return True

    @classmethod
    def create_from_json5(cls, lesson_json5):
        cls.check_json5(lesson_json5)

        lesson = json5.loads(lesson_json5)

        # delete old lesson, all its tasks and progress if it already exists
        # TODO: This is most probably not suited for production use! Replace by activation status for lessons
        try:
            Lesson.objects.get(lesson_id=lesson["id"]).delete()
        except Lesson.DoesNotExist:
            pass
        
        # TODO: create domain model for the lesson

        lsn = Lesson(name=lesson["name"],
                     lesson_id=lesson["id"],
                     author=lesson["author"],
                     text=lesson["text"],
                     text_source=lesson["text_source"],
                     text_licence=lesson["text_licence"],
                     text_url=lesson["text_url"],
                     json5=lesson_json5)
        if 'series' in lesson:
            lsn.series = str(lesson['series'])
        if 'start' in lesson:
            lsn.start = str(lesson['start'])
        if 'wrapup' in lesson:
            lsn.wrapup = str(lesson['wrapup'])

        lsn.save()


        for task in lesson["tasks"]:
            t = Task.create_from_json5(task, lsn)

            
            # check if task is in TaskDifficulty, if not add
            try: 
                TaskDifficulty.objects.get(task=t)
            except TaskDifficulty.DoesNotExist:
                # initialize all new task with difficulty level 1
                new_difficulty = TaskDifficulty(task=t, level=1)
                new_difficulty.save()


        return lsn
    

class Task(models.Model):      # same here 
    """
    There are multiple Tasks within a lesson
    The Tasks are subclassed according to their interaction type


    interaction: in what way does the Leaner give their answer
    type: which of the three different types does the task have, useful for later defining order
    title: the unique identifier of the Task
    paragraph_shown: if true the paragraph for the corresponding lesson will be displayed
    """
    TASK_TYPE = [
        ('R', 'Reading'),
        ('GS', 'Grammar/Style'),
        ('V', 'Vocabulary')
    ]

    name = models.CharField(max_length=256)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    interaction = models.CharField(max_length=10)
    type = models.CharField(max_length=100, choices=TASK_TYPE)
    primary = models.BooleanField(default=True)
    show_lesson_text = models.BooleanField(default=True)
    question = models.TextField()
    content = models.JSONField()
    

    @classmethod
    def check_json5(cls, task_json5, task_num=0):

        for task_field in [("name", str, "a string"),
                           ("type", ['R', 'GS', 'V'], "'R', 'GS', 'V'"),
                           ("interaction", TaskTypeFactory.shortcuts(), ','.join(TaskTypeFactory.shortcuts())),
                           ("primary", bool, "true or false"),
                           ("show_lesson_text", bool, "true or false"),
                           ("question", str, "a string")]: 
            if task_field[0] not in task_json5:
                raise Json5ParseException(
                    'Field "{}" is missing for task {}'.format(task_field[0], task_num))
            if isinstance(task_field[1], type) and not isinstance(task_json5[task_field[0]], task_field[1]):
                raise Json5ParseException(
                    'Field "{}" for task {} has wrong type, it has to be {}'.format(
                        task_field[0], task_num, task_field[2]))
            elif isinstance(task_field[1], list) and task_json5[task_field[0]] not in task_field[1]:
                raise Json5ParseException('Field "{}" for task {} has wrong value, it has to be one of {}'.format(
                    task_field[0], task_num, task_field[2]))

        # fetch the class for that interaction and let it check the json5 content
        TaskTypeFactory.getClass(task_json5['interaction']).check_json5(task_json5, task_num)

        return True

    @classmethod
    def create_from_json5(cls, task, lesson):
        content = TaskTypeFactory.getClass(task['interaction']).get_content_from_json5(task)
        t = Task(name=task["name"],
                 type=task["type"],
                 interaction=task["interaction"],
                 primary=task["primary"],
                 show_lesson_text=task["show_lesson_text"],
                 question=task["question"],
                 content=content,
                 lesson=lesson
                 )
        t.save()
        return t

    def get_template(self):
        return TaskTypeFactory.getClass(self.interaction).template

    def get_additional_js(self):
        try:
            return TaskTypeFactory.getClass(self.interaction).additional_js
        except AttributeError:
            return ''

class UserLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['user', 'lesson']


class Solution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    solved = models.BooleanField()
    analysis = models.JSONField()

class LearnerStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_lesson = models.ForeignKey(Lesson, null=True, on_delete=models.SET_NULL)


class TaskDifficulty(models.Model):

    # define difficulty levels
    class DifficultyLevels(models.IntegerChoices):
        EASY = 1
        MEDIUM = 2
        HARD = 3
        MASTER = 4

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    level = models.IntegerField(choices=DifficultyLevels.choices)
    

    @classmethod
    def update_task_difficulty(cls, task):

        td = TaskDifficulty.objects.get(task=task)
        curr_difficulty= td.level
        feedback = True
        change = 0

        try:
            knowlege = list(DifficultyFeedback.objects.filter(task=task).values_list("knowledge", flat=True))
            redo_count = list(DifficultyFeedback.objects.filter(task=task).values_list("redo_count", flat=True))
        except ValueError:
            feedback = False
            knowlege=[]
            redo_count=[]
        
        
        # calculate feedback

        if feedback:
            for entry in range(len(knowlege)):

                diff = knowlege[entry] - curr_difficulty 
                nr_redo = redo_count[entry]
                
                # wenn diff < 0 bedeutet: task war schwerer als knowledge
                # wenn diff > 0 bedeutet: task war leichter 
                # wenn diff == 0 bedeutet: task war angemessen

                # wenn task leichter und redo > 1 -> change + diff
                # wenn task angemessen und redo > 1 -> change + 0
                # wenn task schwer und redo < 1 -> change -diff

                if diff > 0 and nr_redo > 1:
                    change += diff
                
                if diff < 0 and nr_redo == 0:
                    change += diff

                if diff == 0 and nr_redo > 1:
                    change += 1
                
                if diff == 0 and nr_redo > 3:
                    change += 2
                    
            new_difficulty = int(curr_difficulty + change/len(knowlege))
            curr_difficulty = new_difficulty
            if curr_difficulty < 1:
                curr_difficulty = 1
            if curr_difficulty > 4:
                curr_difficulty = 4
        td.level = curr_difficulty
        td.save()
        # delete all existing rows in Difficulty feedback
        #DifficultyFeedback.objects.filter(task=task).delete()
        return True
    
    @classmethod
    def update_next_task(cls, task, ita_list:list):

        # get TaskDifficulty for the task:
        td = TaskDifficulty.objects.get(task=task)
        
        next_tasks = ""

        # make a string out of the ita_list 
        for task in range(len(ita_list)):
            next_tasks += str(ita_list[task])
            next_tasks += ","
        
        # save the string as td.next_tasks
        td.next_tasks = next_tasks
        td.save()

        return True



class LearnerKnowledgeLevel(models.Model):

    # define knowledge level
    class KnowledgeLevels(models.IntegerChoices):
        EASY = 1
        BEGINNER = 2
        INTERMEDIATE = 3
        ADVANCED = 4
        MASTERY = 5
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    level = models.IntegerField(choices=KnowledgeLevels.choices, default=1)

    


class DifficultyFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    difficulty = models.IntegerField(default=1)
    knowledge = models.IntegerField(default=1)       
    redo_count = models.IntegerField(default=0)
    ita_feedback = models.IntegerField(default=1)

    @classmethod
    def prepare_ita_data(cls, user):
        # get the data of the user

        # fuer ita: datasets -> by user and task difficulty -> tasks and ita_feedback
        try:
            DifficultyFeedback.objects.get(user=user)
        except ValueError:
            print("User ", user, " is invalid!")
            return
        
        df = pd.DataFrame(list(DifficultyFeedback.objects.filter(user=user).values("task", "difficulty", "ita_feedback")))
        level_1 = df[df["difficulty"] == 1].iloc[:, ["task", "ita_feedback"]]
        level_2 = df[df["difficulty"] == 2].iloc[:, ["task", "ita_feedback"]]
        level_3 = df[df["difficulty"] == 3].iloc[:, ["task", "ita_feedback"]]
        level_4 = df[df["difficulty"] == 4].iloc[:, ["task", "ita_feedback"]]

        return level_1, level_2, level_3, level_4


# this might be really not elegant but I have to solve the redo problem somehow
class RedoThisTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, default=None)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    redo = models.BooleanField(default=False)

class Counter(models.Model):
    counter = models.IntegerField(default=0)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)