"""ipaca Learner Model

The learner model maintains a model about a given learner's competencies.

"""

from .tasks import TaskTypeFactory
from learning_environment.models import Solution, LearnerKnowledgeLevel, TaskDifficulty, DifficultyFeedback

class Learnermodel:

    def __init__(self, learner):
        """Initializes the learner model for a given learner.

        learner: User object"""

        self.learner = learner

    def update(self, task, solution):
        """Updates the learner model by analyzing the solution for a task.

        task: Task object
        solution: Dictionary with solution (usually form data from POST request)

        Return a tuple of analysis dictionary and context dictionary"""

        analyzer = TaskTypeFactory.getObject(task)
        (analysis, context) = analyzer.analyze_solution(solution)

        # Save solution and analysis to database
        solution = Solution(user=self.learner, task=task, solved=analysis.get('solved', False), analysis=analysis)
        solution.save()
        
        lesson=task.lesson
        
        # TODO: update knowledge level of learner

        # create message
        if analysis.get('solved', False):
            context['msg'] = "Congratulation! That's correct!"
            
            # update score and/or level
            try:
                lkl= LearnerKnowledgeLevel.objects.get(user=self.learner, lesson=lesson)
                knowledge=lkl.level
            except LearnerKnowledgeLevel.DoesNotExist:
                LearnerKnowledgeLevel.objects.create(user=self.learner, lesson=lesson, level=1, score=0)
                knowledge=1
            try:
                redo_count = DifficultyFeedback.objects.get(user=self.learner, task=task).redo_count
            except (DifficultyFeedback.DoesNotExist, ValueError):
                DifficultyFeedback.objects.create(user=self.learner, task=task, difficulty=TaskDifficulty.objects.get(task=task).level, knowledge=knowledge, redo_count=0, ita_feedback=1)
                redo_count=0

            if redo_count==0:
                lkl.score+=1
                if lkl.score == 5:
                    lkl.level+=1
                    lkl.score=0
                lkl.save()

            
        else:
            context['msg'] = "Oh no, that's not correct."
            # try: feedback redo count -> if not initialize with 0, +=1

            try:
                lkl=LearnerKnowledgeLevel.objects.get(user=self.learner, lesson=lesson)
            except LearnerKnowledgeLevel.DoesNotExist:
                LearnerKnowledgeLevel.objects.create(user=self.learner, lesson=lesson, level=1, score=0)
                lkl=LearnerKnowledgeLevel(user=self.learner, lesson=lesson)

            try:
                df=DifficultyFeedback.objects.get(user=self.learner, task=task)
                df.redo_count+=1
                df.ita_feedback=0
                df.save()
            except (DifficultyFeedback.DoesNotExist, ValueError):
                DifficultyFeedback.objects.create(user=self.learner, task=task, difficulty=TaskDifficulty.objects.get(task=task).level, knowledge=lkl.level, redo_count=1, ita_feedback=0)

            
            
        return analysis, context
