from rest_framework import serializers

from .models import TeacherProfile, TimetableEntry


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = ['id']


class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time >= end_time:
            raise serializers.ValidationError('start_time must be before end_time.')

        school = attrs.get('school')
        teacher = attrs.get('teacher')
        weekday = attrs.get('weekday')
        class_name = attrs.get('class_name')
        section = attrs.get('section', '')
        room = attrs.get('room', '')

        queryset = TimetableEntry.objects.filter(school=school, weekday=weekday)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        overlapping = queryset.filter(start_time__lt=end_time, end_time__gt=start_time)
        if overlapping.filter(teacher=teacher).exists():
            raise serializers.ValidationError('Teacher has an overlapping class slot.')
        if overlapping.filter(class_name=class_name, section=section).exists():
            raise serializers.ValidationError('Class has an overlapping timetable slot.')
        if room and overlapping.filter(room=room).exists():
            raise serializers.ValidationError('Room is already occupied during this time slot.')

        return attrs
