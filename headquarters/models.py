from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from tenants.models import SchoolTenant

User = get_user_model()


class UserProfile(models.Model):
	ROLE_CHOICES = [
		('HQ', 'Headquarters'),
		('PRINCIPAL', 'Principal'),
		('TEACHER', 'Teacher'),
		('STUDENT', 'Student'),
		('PARENT', 'Parent'),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
	role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='PARENT')
	school = models.ForeignKey(SchoolTenant, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')

	def __str__(self):
		return f'{self.user.username} ({self.role})'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
