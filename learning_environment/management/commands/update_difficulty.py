from django.core.management.base import BaseCommand, CommandError
import glob
import re
from models import TaskDifficulty, DifficultyFeedback

"""
Command for updating the difficulty levels of the tasks

"""

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        nr_updates = 0
        # für alle task in taskdifficultylevel
        for task in TaskDifficulty.objects.get(task):
            try:
                DifficultyFeedback.objects.get(task=task)
            except DifficultyFeedback.DoesNotExist:
                print("DifficultyFeedback must exist to update difficulties")

        self.stdout.write(self.style.SUCCESS('Successfully updated {} task difficulties.'.format(nr_updates)))
        