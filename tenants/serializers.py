from rest_framework import serializers

from .models import SchoolTenant


class SchoolOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolTenant
        fields = ['id', 'name', 'subdomain', 'contact_email', 'subscription_status', 'schema_name']
        read_only_fields = ['id', 'subscription_status', 'schema_name']
