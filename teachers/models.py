from django.db import models

from tenants.models import SchoolTenant


class TeacherProfile(models.Model):
	school = models.ForeignKey(SchoolTenant, on_delete=models.CASCADE, related_name='teachers')
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	employee_id = models.CharField(max_length=64)
	subjects = models.JSONField(default=list)
	assigned_classes = models.JSONField(default=list)

	class Meta:
		unique_together = [('school', 'employee_id')]
		ordering = ['first_name', 'last_name']

	def __str__(self):
		return f'{self.first_name} {self.last_name}'


class TimetableEntry(models.Model):
	WEEKDAY_CHOICES = [
		(1, 'Monday'),
		(2, 'Tuesday'),
		(3, 'Wednesday'),
		(4, 'Thursday'),
		(5, 'Friday'),
		(6, 'Saturday'),
		(7, 'Sunday'),
	]

	school = models.ForeignKey(SchoolTenant, on_delete=models.CASCADE, related_name='timetable_entries')
	teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='timetable_entries')
	class_name = models.CharField(max_length=32)
	section = models.CharField(max_length=32, blank=True)
	subject = models.CharField(max_length=128)
	room = models.CharField(max_length=64, blank=True)
	weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
	start_time = models.TimeField()
	end_time = models.TimeField()

	class Meta:
		ordering = ['weekday', 'start_time']

	def __str__(self):
		return f'{self.class_name} {self.subject} ({self.weekday})'
