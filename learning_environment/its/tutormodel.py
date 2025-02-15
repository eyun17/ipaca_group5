"""ipaca Tutor Model

The tutor model is able to determine appropriate actions for a given learner. (E.g. generate a 'next task')

"""

import random
from learning_environment.models import Lesson, Task, ProfileSeriesLevel, TaskDifficulty, LearnerKnowledgeLevel, DifficultyFeedback, Counter, NextTask
from django.http import HttpResponseBadRequest

class NoTaskAvailableError(Exception):
    pass


class Tutormodel:

    def __init__(self, learner):
        """Initializes the tutor model for a given learner.
        learner: User object"""
        self.learner = learner

    def next_task(self, request):
        """Pick a next task for the learner.
        Returns tuple:
        (STATE, lesson, task)
        """
        

        # TODO: other order
        # we have to change the order, if not we only do one task per lesson an then the wrapup
        order = ['START', 'R', 'GS', 'V', 'WRAPUP']
        order1 =['R', 'GS', 'V']
        order2 = ['R','GS','R', 'WRAPUP']
        # determine the current lesson series
        series = request.session.get('lesson_series', 'General')

        # pick a lesson
        current_lesson_id = request.session.get('current_lesson', None)
        if current_lesson_id:
            try:
                lesson = Lesson.objects.get(pk=current_lesson_id)
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))
        else:
            lesson = self.start_lesson(series)
            request.session['current_lesson'] = lesson.id
            request.session['current_lesson_todo'] = order[:]
            request.session.modified = True

        # when there is a task for this lesson in redo, redo the task
        try:
            redo = NextTask.objects.get(user=request.user, lesson=lesson).redo
            str_next_task = NextTask.objects.get(user=request.user, lesson=lesson).next_task
        except (NextTask.DoesNotExist, ValueError):
            redo = False
            str_next_task = ""
        
        if redo:
            task_id = NextTask.objects.get(user=request.user, lesson=lesson, redo=True).task.id
            try:
                task = Task.objects.get(id = task_id)
            except KeyError:
                return HttpResponseBadRequest("Error: No such ID")
            lesson = task.lesson
            state = task.type
            return state, lesson, task

        try:
            count = Counter.objects.get(user=request.user, lesson=lesson)
        except (Counter.DoesNotExist, ValueError):
            Counter.objects.create(user=request.user, lesson=lesson, counter=0)
            count = Counter.objects.get(user=request.user, lesson=lesson)

        try: 
            lkl = LearnerKnowledgeLevel.objects.get(user=request.user, lesson=lesson)
        except ValueError:
            LearnerKnowledgeLevel.objects.create(user=request.user, lesson=lesson, level=1, score=0)
            lkl = LearnerKnowledgeLevel.objects.get(user=request.user, lesson=lesson)

        # when master
        if lkl.level == 5 or count.counter >= 3:
            request.session['current_lesson_todo'] = ['WRAPUP']
            request.session.modified = True
        
        if str_next_task is not "":
            lst_next_task = [int(nt_id) for nt_id in str_next_task.split(",")]
            higher = []
            lower = []
            equal = []

            if len(lst_next_task) == 1:
                try:
                    task = Task.objects.get(id = entry)
                except KeyError:
                    return HttpResponseBadRequest("Error: No such ID")
                
                return(task.type, task.lesson, task)

            for entry in range(len(lst_next_task)):
                try:
                    task = Task.objects.get(id = entry)
                except KeyError:
                    return HttpResponseBadRequest("Error: No such ID")

                difficulty = TaskDifficulty.objects.get(task=task.id).level

                if lkl.level == difficulty:
                    equal.append(task)
                
                elif lkl.level > difficulty:
                    higher.append(task)
                
                else:
                    lower.append(task)
            
            list_all = [equal, lower, higher]
            choice = random.choices(list_all, weights=(85, 10, 5), k=1)[0]
            cnt = len(choice)
            task = choice[random.randint(0, cnt-1)]

            return (task.type, task.lesson, task)


        # pick a task according to knowledge level -> difficulty level of task
        while 1:
            next_type = request.session['current_lesson_todo'][0]
            request.session.modified = True
            if next_type == 'START':
                request.session['current_lesson_todo'] = order1[:]
                request.session.modified = True
                return next_type, lesson, None

            elif next_type == 'WRAPUP':
                return next_type, lesson, None

            else:  
                possible_tasks = Task.objects.filter(lesson=lesson, type=next_type)
                task_list = []
                
                for task in possible_tasks:
                    difficulty = TaskDifficulty.objects.get(task=task.id).level

                    # was task successfully done
                    try:
                        DifficultyFeedback.objects.get(user = self.learner, task=task)
                        success = True
                    except (DifficultyFeedback.DoesNotExist, ValueError):
                        success = False

                    if (difficulty == lkl.level) and not(success):
                        task_list.append(task)


                request.session['current_lesson_todo'].extend(order1)
                request.session.modified = True
                
                cnt = len(task_list)
                if cnt == 0:
                    request.session['current_lesson_todo'].pop(0) 
                    request.session['current_lesson_todo'].extend(order1)
                    request.session.modified = True
                    count.counter += 1
                    if count.counter >= 3:
                        request.session['current_lesson_todo'] = ['WRAPUP']
                        request.session.modified = True
                    count.save()
                    continue  # next state
                    
                # if the task list is not empty reset the counter
                count.counter = 0
                count.save()
                task = task_list[random.randint(0, cnt-1)]
    
                return next_type, lesson, task

        
    def start_lesson(self, series):
        try:
            current_level = ProfileSeriesLevel.objects.get(user=self.learner, series=series).level
        except ProfileSeriesLevel.DoesNotExist:
            ProfileSeriesLevel.objects.create(user=self.learner, series=series, level=0)
            current_level = 0

        
        lesson = Lesson.objects.filter(series=series).order_by("lesson_id")[current_level]

        # check whether LearnerKnowledgeLevel exists for this lesson
        
        try:
            LearnerKnowledgeLevel.objects.get(user=self.learner, lesson=lesson).level
        except (LearnerKnowledgeLevel.DoesNotExist, ValueError):
            LearnerKnowledgeLevel.objects.create(user=self.learner, lesson=lesson, level=1, score=0)
        
        return lesson
