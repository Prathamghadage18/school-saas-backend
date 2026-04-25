from django.db import models
from django.conf import settings

from tenants.models import SchoolTenant


class StudentProfile(models.Model):
	school = models.ForeignKey(SchoolTenant, on_delete=models.CASCADE, related_name='students')
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	admission_number = models.CharField(max_length=64)
	class_name = models.CharField(max_length=32)
	section = models.CharField(max_length=32, blank=True)
	parent_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='children',
	)
	date_of_birth = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = [('school', 'admission_number')]
		ordering = ['first_name', 'last_name']

	def __str__(self):
		return f'{self.first_name} {self.last_name}'


class AttendanceRecord(models.Model):
	STATUS_CHOICES = [
		('PRESENT', 'Present'),
		('ABSENT', 'Absent'),
		('LATE', 'Late'),
	]

	school = models.ForeignKey(SchoolTenant, on_delete=models.CASCADE, related_name='attendance_records')
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
	marked_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='attendance_marked',
	)
	attendance_date = models.DateField()
	status = models.CharField(max_length=16, choices=STATUS_CHOICES)
	remarks = models.CharField(max_length=255, blank=True)

	class Meta:
		unique_together = [('student', 'attendance_date')]
		ordering = ['-attendance_date']

	def __str__(self):
		return f'{self.student} - {self.attendance_date} - {self.status}'
