from django.db import models

# Create your models here.
class ExampleModel(models.Model):
	name = models.CharField(max_length=128)
	number = models.PositiveIntegerField()
	description = models.TextField()

	def __unicode__(self):
		return self.name