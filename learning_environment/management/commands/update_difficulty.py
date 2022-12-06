from django.core.management.base import BaseCommand, CommandError
import glob
import re
from learning_environment.models import TaskDifficulty, DifficultyFeedback

"""
Command for updating the difficulty levels of the tasks

"""

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        nr_updates = 0
        delete=0
        # für alle task in taskdifficultylevel
        try:
            tasks_to_update = DifficultyFeedback.objects.values_list("task", flat=True)
        except (DifficultyFeedback.DoesNotExist, ValueError):
            print("something went wrong!")
            tasks_to_update=[]
        
        # update all tasks
        for task in tasks_to_update:
            try:
                TaskDifficulty.update_task_difficulty(task=task)
                nr_updates+=1
            except ValueError:
                pass

        DifficultyFeedback.objects.all().delete()   
        

        self.stdout.write(self.style.SUCCESS('Successfully updated {} task difficulties.'.format(nr_updates)))
        