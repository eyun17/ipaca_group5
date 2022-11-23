"""ipaca Tutor Model

The tutor model is able to determine appropriate actions for a given learner. (E.g. generate a 'next task')

"""

import random
from learning_environment.models import Lesson, Task, ProfileSeriesLevel, TaskDifficulty, LearnerKnowledgeLevel


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

        try: 
            lkl = LearnerKnowledgeLevel.objects.get(user=request.user, lesson=lesson)
        except ValueError:
            LearnerKnowledgeLevel.objects.create(user=request.user, lesson=lesson, level=1, score=0)
            lkl = LearnerKnowledgeLevel.objects.get(user=request.user, lesson=lesson)

        # when master
        if lkl.level == 5:
            request.session['current_lesson_todo'] = ['WRAPUP']
            request.session.modified = True
        
        empty_count=0
        # TODO: get the knowledge level of the learner
        # pick a task according to knowledge level -> difficulty level of task
        while 1:
            next_type = request.session['current_lesson_todo'][0]
            request.session.modified = True
            if next_type == 'START':
                request.session['current_lesson_todo'] = order1[:]
                request.session.modified = True
                print(request.session['current_lesson_todo'])
                return next_type, lesson, None

            elif next_type == 'WRAPUP':
                return next_type, lesson, None
            else:  
                possible_tasks = Task.objects.filter(lesson=lesson, type=next_type)
                task_list = []
                print(possible_tasks)
                for task in possible_tasks:
                    difficulty = TaskDifficulty.objects.get(task=task.id).level
                    print("d", difficulty)
                    print("k", lkl.level)
                    if difficulty == lkl.level:
                        print("in task_list.append")
                        task_list.append(task)
                request.session['current_lesson_todo'].extend(order1)
                request.session.modified = True
                print(task_list)
                cnt = len(task_list)
                if cnt == 0:
                    print("in cnt==0")
                    empty_count+=1
                    request.session['current_lesson_todo'].pop(0) 
                    request.session['current_lesson_todo'].extend(order1) 

                    # if the knowledge level is at mastery or there are no more tasks available do wrapup
                    if lkl.level==5 or empty_count==3:
                        request.session['current_lesson_todo'] = ['WRAPUP']

                    request.session.modified = True
                    continue  # next state
                task = task_list[random.randint(0, cnt-1)]
                print(task)
               
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
