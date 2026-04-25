from rest_framework import serializers

from .models import AttendanceRecord, StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        read_only_fields = ['id', 'marked_by']


class StudentAttendanceSummarySerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
