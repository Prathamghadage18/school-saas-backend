from django.db.models import Count, Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsTeacherOrAbove, get_user_role, get_user_school
from .models import AttendanceRecord, StudentProfile
from .serializers import (
	AttendanceRecordSerializer,
	StudentAttendanceSummarySerializer,
	StudentProfileSerializer,
)


class StudentProfileViewSet(viewsets.ModelViewSet):
	serializer_class = StudentProfileSerializer
	queryset = StudentProfile.objects.select_related('school', 'parent_user').all()
	search_fields = ['first_name', 'last_name', 'admission_number', 'class_name']
	filterset_fields = ['class_name', 'section', 'school']

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
		if role == 'PARENT':
			return queryset.filter(parent_user=self.request.user)
		if school:
			return queryset.filter(school=school)
		return queryset.none()

	def perform_create(self, serializer):
		school = serializer.validated_data.get('school') or get_user_school(self.request.user)
		serializer.save(school=school)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
	serializer_class = AttendanceRecordSerializer
	queryset = AttendanceRecord.objects.select_related('student', 'school', 'marked_by').all()
	filterset_fields = ['school', 'student', 'status', 'attendance_date']

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
		if role == 'PARENT':
			return queryset.filter(student__parent_user=self.request.user)
		if school:
			return queryset.filter(school=school)
		return queryset.none()

	def perform_create(self, serializer):
		school = serializer.validated_data.get('school') or get_user_school(self.request.user)
		serializer.save(marked_by=self.request.user, school=school)

	@action(detail=False, methods=['get'], url_path='summary')
	def summary(self, request):
		queryset = self.get_queryset()
		student_id = request.query_params.get('student_id')
		if student_id:
			queryset = queryset.filter(student_id=student_id)

		aggregate = queryset.aggregate(
			total_days=Count('id'),
			present_days=Count('id', filter=Q(status='PRESENT')),
		)
		total = aggregate['total_days'] or 0
		present = aggregate['present_days'] or 0
		percentage = round((present / total) * 100, 2) if total else 0.0

		payload = {
			'student_id': int(student_id) if student_id else 0,
			'total_days': total,
			'present_days': present,
			'attendance_percentage': percentage,
		}
		serializer = StudentAttendanceSummarySerializer(payload)
		return Response(serializer.data)
