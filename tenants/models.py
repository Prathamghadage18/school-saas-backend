from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class SchoolTenant(TenantMixin):
	SUBSCRIPTION_CHOICES = [
		('TRIAL', 'Trial'),
		('ACTIVE', 'Active'),
		('PAST_DUE', 'Past Due'),
		('CANCELED', 'Canceled'),
	]

	name = models.CharField(max_length=255)
	subdomain = models.SlugField(max_length=63, unique=True)
	contact_email = models.EmailField(blank=True)
	stripe_customer_id = models.CharField(max_length=128, blank=True)
	stripe_subscription_id = models.CharField(max_length=128, blank=True)
	subscription_status = models.CharField(max_length=16, choices=SUBSCRIPTION_CHOICES, default='TRIAL')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	# Keep false by default for local MVP where sqlite may be used.
	auto_create_schema = False

	def save(self, *args, **kwargs):
		if not self.schema_name:
			self.schema_name = self.subdomain.replace('-', '_')
		super().save(*args, **kwargs)

	def __str__(self):
		return f'{self.name} ({self.schema_name})'


class SchoolDomain(DomainMixin):
	pass
