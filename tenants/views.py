from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
import stripe

from core.permissions import IsHQ
from .models import SchoolDomain, SchoolTenant
from .serializers import SchoolOnboardingSerializer


class SchoolTenantViewSet(viewsets.ModelViewSet):
	queryset = SchoolTenant.objects.all().order_by('-created_at')
	serializer_class = SchoolOnboardingSerializer

	def get_permissions(self):
		if self.action == 'create':
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated(), IsHQ()]

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		tenant = serializer.save()

		# For local development, domain defaults to localhost subdomain style.
		domain_value = request.data.get('domain') or f"{tenant.subdomain}.localhost"
		SchoolDomain.objects.get_or_create(domain=domain_value, tenant=tenant, defaults={'is_primary': True})

		if settings.STRIPE_SECRET_KEY:
			stripe.api_key = settings.STRIPE_SECRET_KEY
			customer = stripe.Customer.create(
				name=tenant.name,
				email=tenant.contact_email or None,
				metadata={'tenant_subdomain': tenant.subdomain},
			)
			tenant.stripe_customer_id = customer.id
			tenant.save(update_fields=['stripe_customer_id'])

		response_data = self.get_serializer(tenant).data
		response_data['domain'] = domain_value
		return Response(response_data, status=status.HTTP_201_CREATED)
