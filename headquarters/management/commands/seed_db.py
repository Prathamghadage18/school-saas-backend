from datetime import timedelta
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from headquarters.models import UserProfile
from students.models import AttendanceRecord, StudentProfile
from tenants.models import SchoolDomain, SchoolTenant
from teachers.models import TeacherProfile, TimetableEntry

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with demo data for all roles and schools'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        schools = []
        school_names = [
            ('riverside-high', 'Riverside High School', 'admin@riverside.edu'),
            ('central-academy', 'Central Academy', 'admin@central.edu'),
            ('oak-valley', 'Oak Valley School', 'admin@oak.edu'),
        ]

        for subdomain, name, email in school_names:
            school, created = SchoolTenant.objects.get_or_create(
                subdomain=subdomain,
                defaults={
                    'name': name,
                    'contact_email': email,
                    'schema_name': subdomain.replace('-', '_'),
                    'subscription_status': 'ACTIVE',
                    'is_active': True,
                },
            )
            schools.append(school)
            if created:
                SchoolDomain.objects.get_or_create(
                    domain=f'{subdomain}.localhost',
                    tenant=school,
                    defaults={'is_primary': True},
                )
                self.stdout.write(f'  ✓ Created school: {name}')
            else:
                self.stdout.write(f'  • School exists: {name}')

        hq_user, created = User.objects.get_or_create(
            username='hq_admin',
            defaults={
                'email': 'hq@company.com',
                'first_name': 'Admin',
                'last_name': 'User',
            },
        )
        if created:
            hq_user.set_password('testpass123')
            hq_user.save()
        hq_user.user_profile.role = 'HQ'
        hq_user.user_profile.save()
        self.stdout.write('  ✓ HQ Admin: hq_admin / testpass123')

        for school in schools:
            self.stdout.write(f'\n📚 Setting up {school.name}...')

            principal_user, created = User.objects.get_or_create(
                username=f'principal_{school.subdomain}',
                defaults={
                    'email': f'principal@{school.subdomain}.edu',
                    'first_name': 'Principal',
                    'last_name': school.name.split()[0],
                },
            )
            if created:
                principal_user.set_password('testpass123')
                principal_user.save()
            principal_user.user_profile.role = 'PRINCIPAL'
            principal_user.user_profile.school = school
            principal_user.user_profile.save()
            self.stdout.write(f'    ✓ Principal: principal_{school.subdomain}')

            teachers = []
            teacher_names = [
                ('Alice', 'Johnson', ['Math', 'Science']),
                ('Bob', 'Smith', ['English', 'History']),
            ]
            for first, last, subjects in teacher_names:
                teacher_user, created = User.objects.get_or_create(
                    username=f'teacher_{school.subdomain}_{first.lower()}',
                    defaults={
                        'email': f'{first.lower()}@{school.subdomain}.edu',
                        'first_name': first,
                        'last_name': last,
                    },
                )
                if created:
                    teacher_user.set_password('testpass123')
                    teacher_user.save()
                teacher_user.user_profile.role = 'TEACHER'
                teacher_user.user_profile.school = school
                teacher_user.user_profile.save()

                teacher_profile, _ = TeacherProfile.objects.get_or_create(
                    school=school,
                    employee_id=f'{school.subdomain}_T{len(teachers)+1}',
                    defaults={
                        'first_name': first,
                        'last_name': last,
                        'subjects': subjects,
                        'assigned_classes': ['10A', '10B'],
                    },
                )
                teachers.append((teacher_user, teacher_profile))
                self.stdout.write(f'      ✓ Teacher: {first} {last} ({", ".join(subjects)})')

            if teachers:
                teacher_profile = teachers[0][1]
                for idx, day in enumerate([1, 2, 3, 4, 5]):
                    TimetableEntry.objects.get_or_create(
                        school=school,
                        teacher=teacher_profile,
                        weekday=day,
                        class_name='10A',
                        defaults={
                            'subject': 'Math',
                            'room': 'Room 101',
                            'start_time': f'{9 + idx}:00:00',
                            'end_time': f'{10 + idx}:00:00',
                        },
                    )
                self.stdout.write(f'      ✓ Timetable created for {teachers[0][0].first_name}')

            students_data = [
                ('John', 'Doe', 'STUDENT_001'),
                ('Jane', 'Smith', 'STUDENT_002'),
                ('Michael', 'Brown', 'STUDENT_003'),
            ]
            for first, last, adm_no in students_data:
                parent_user, created = User.objects.get_or_create(
                    username=f'parent_{school.subdomain}_{first.lower()}',
                    defaults={
                        'email': f'parent_{first.lower()}@{school.subdomain}.edu',
                        'first_name': f'Parent of {first}',
                        'last_name': last,
                    },
                )
                if created:
                    parent_user.set_password('testpass123')
                    parent_user.save()
                parent_user.user_profile.role = 'PARENT'
                parent_user.user_profile.school = school
                parent_user.user_profile.save()

                student_user, created = User.objects.get_or_create(
                    username=f'student_{school.subdomain}_{first.lower()}',
                    defaults={
                        'email': f'student_{first.lower()}@{school.subdomain}.edu',
                        'first_name': first,
                        'last_name': last,
                    },
                )
                if created:
                    student_user.set_password('testpass123')
                    student_user.save()
                student_user.user_profile.role = 'STUDENT'
                student_user.user_profile.school = school
                student_user.user_profile.save()

                student_profile, _ = StudentProfile.objects.get_or_create(
                    school=school,
                    admission_number=adm_no,
                    defaults={
                        'first_name': first,
                        'last_name': last,
                        'class_name': '10A',
                        'section': 'A',
                        'parent_user': parent_user,
                    },
                )

                today = timezone.now().date()
                for i in range(20):
                    date = today - timedelta(days=20 - i)
                    status = random.choice(['PRESENT', 'PRESENT', 'PRESENT', 'ABSENT'])
                    AttendanceRecord.objects.get_or_create(
                        school=school,
                        student=student_profile,
                        attendance_date=date,
                        defaults={
                            'status': status,
                            'marked_by': teachers[0][0] if teachers else principal_user,
                        },
                    )

                self.stdout.write(
                    f'      ✓ Student: {first} {last} | Parent: parent_{school.subdomain}_{first.lower()} | Attendance: 20 days seeded'
                )

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeding complete!\n'))
        self.stdout.write(self.style.WARNING('Demo Credentials:\n'))
        self.stdout.write('HQ User:')
        self.stdout.write('  Username: hq_admin')
        self.stdout.write('  Password: testpass123\n')

        for school in schools:
            self.stdout.write(f'{school.name}:')
            self.stdout.write(f'  Principal: principal_{school.subdomain} / testpass123')
            self.stdout.write(f'  Teacher: teacher_{school.subdomain}_alice / testpass123')
            self.stdout.write(f'  Student: student_{school.subdomain}_john / testpass123')
            self.stdout.write(f'  Parent: parent_{school.subdomain}_john / testpass123\n')
