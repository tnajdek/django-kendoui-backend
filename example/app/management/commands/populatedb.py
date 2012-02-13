from django.core.management.base import BaseCommand, CommandError
from app.utils import get_random_entry

class Command(BaseCommand):
	def handle(self, *args, **options):
		for i in range(1000):
			entry = get_random_entry()
			entry.save()
