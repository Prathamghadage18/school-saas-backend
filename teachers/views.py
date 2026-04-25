from rest_framework import permissions, viewsets

from core.permissions import IsTeacherOrAbove, get_user_role, get_user_school
from .models import TeacherProfile, TimetableEntry
from .serializers import TeacherProfileSerializer, TimetableEntrySerializer


class TeacherProfileViewSet(viewsets.ModelViewSet):
	serializer_class = TeacherProfileSerializer
	queryset = TeacherProfile.objects.select_related('school').all()
	search_fields = ['first_name', 'last_name', 'employee_id']
	filterset_fields = ['school']

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsTeacherOrAbove()]

	def get_queryset(self):
		queryset = super().get_queryset()
		role = get_user_role(self.request.user)
		school = get_user_school(self.request.user)
		if role == 'HQ':
			return queryset
		if school:
			return queryset.filter(school=school)
		return queryset.none()

	def perform_create(self, serializer):
		school = serializer.validated_data.get('school') or get_user_school(self.request.user)
		serializer.save(school=school)


class TimetableEntryViewSet(viewsets.ModelViewSet):
	serializer_class = TimetableEntrySerializer
	queryset = TimetableEntry.objects.select_related('school', 'teacher').all()
	filterset_fields = ['school', 'teacher', 'weekday', 'class_name', 'section']

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsTeacherOrAbove()]

	def get_queryset(self):
		queryset = super().get_queryset()
		role = get_user_role(self.request.user)
		school = get_user_school(self.request.user)
		if role == 'HQ':
			return queryset
		if school:
			return queryset.filter(school=school)
		return queryset.none()

	def perform_create(self, serializer):
		school = serializer.validated_data.get('school') or get_user_school(self.request.user)
		serializer.save(school=school)
