from datetime import date, timedelta
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from info.models import (
    Dept, Class, Course, Student, Teacher, Assign, AssignTime,
    AttendanceRange, AttendanceClass, Attendance, StudentCourse, AttendanceTotal,
)

User = get_user_model()

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

TIME_SLOTS = [
    '7:30 - 8:30', '8:30 - 9:30', '9:30 - 10:30', '11:00 - 11:50',
    '11:50 - 12:40', '12:40 - 1:30', '2:30 - 3:30', '3:30 - 4:30', '4:30 - 5:30',
]


def make_user(username, password, first_name, last_name=''):
    user, created = User.objects.get_or_create(username=username)
    user.first_name = first_name
    user.last_name = last_name
    user.set_password(password)
    user.save()
    return user


class Command(BaseCommand):
    help = 'Seed the database with demo admin, students, faculty, courses and timetable.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-attendance',
            action='store_true',
            help='Do not generate random demo attendance records.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding CollegeERP database...')

        # ---------- Admin ----------
        admin, created = User.objects.get_or_create(username='admin')
        admin.set_password('Hitman@4165')
        admin.first_name = 'System'
        admin.last_name = 'Administrator'
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        self.stdout.write('  [OK] Admin user created (admin / Hitman@4165)')

        # ---------- Departments ----------
        depts = {}
        for dept_id, name in [('CSE', 'Computer Science & Engineering'),
                              ('ECE', 'Electronics & Communication Engineering'),
                              ('ME', 'Mechanical Engineering'),
                              ('CIVIL', 'Civil Engineering')]:
            depts[dept_id], _ = Dept.objects.get_or_create(id=dept_id, name=name)
        self.stdout.write('  [OK] 4 departments created')

        # ---------- Classes ----------
        classes = {}
        class_specs = [('CS3A', 'CSE', 3, 'A'), ('CS5A', 'CSE', 5, 'A'),
                       ('EC3A', 'ECE', 3, 'A'), ('ME3A', 'ME', 3, 'A'),
                       ('CIV3A', 'CIVIL', 3, 'A')]
        for cid, dept_id, sem, section in class_specs:
            classes[cid], _ = Class.objects.get_or_create(
                id=cid, dept=depts[dept_id], sem=sem, section=section)
        self.stdout.write('  [OK] 5 classes created')

        # ---------- Courses ----------
        courses = {}
        course_specs = [
            ('CS301', 'CSE', 'Engineering Mathematics III', 'MA'),
            ('CS302', 'CSE', 'Data Structures', 'DS'),
            ('CS303', 'CSE', 'Database Management Systems', 'DBMS'),
            ('CS304', 'CSE', 'Computer Organization', 'CO'),
            ('CS501', 'CSE', 'Operating Systems', 'OS'),
            ('CS502', 'CSE', 'Computer Networks', 'CN'),
            ('CS503', 'CSE', 'Software Engineering', 'SE'),
            ('CS504', 'CSE', 'Web Technologies', 'WT'),
            ('CS505', 'CSE', 'Artificial Intelligence', 'AI'),
            ('EC301', 'ECE', 'Electronic Circuits', 'EC'),
            ('EC302', 'ECE', 'Signals & Systems', 'SS'),
            ('EC303', 'ECE', 'Microprocessors', 'MP'),
            ('ME301', 'ME', 'Engineering Mechanics', 'EM'),
            ('ME302', 'ME', 'Thermodynamics', 'TH'),
            ('CIV301', 'CIVIL', 'Structural Analysis', 'SA'),
            ('CIV302', 'CIVIL', 'Fluid Mechanics', 'FM'),
        ]
        for cid, dept_id, name, short in course_specs:
            courses[cid], _ = Course.objects.get_or_create(
                id=cid, dept=depts[dept_id], name=name, shortname=short)
        self.stdout.write('  [OK] 15 courses created')

        # ---------- Faculty (12) ----------
        teachers = {}
        teacher_specs = [
            ('CS01', 'CSE', 'Anil Kumar', 'Male', '1980-05-12'),
            ('CS02', 'CSE', 'Priya Sharma', 'Female', '1985-08-21'),
            ('CS03', 'CSE', 'Ramesh Patel', 'Male', '1978-01-30'),
            ('CS04', 'CSE', 'Kavita Rao', 'Female', '1986-04-18'),
            ('CS05', 'CSE', 'Deepak Joshi', 'Male', '1981-09-09'),
            ('CS06', 'CSE', 'Neha Gupta', 'Female', '1990-12-01'),
            ('EC01', 'ECE', 'Sunita Verma', 'Female', '1982-11-14'),
            ('EC02', 'ECE', 'Vikram Singh', 'Male', '1988-03-05'),
            ('EC03', 'ECE', 'Rohit Malhotra', 'Male', '1984-06-27'),
            ('ME01', 'ME', 'Suresh Reddy', 'Male', '1983-07-19'),
            ('ME02', 'ME', 'Farhan Khan', 'Male', '1987-02-14'),
            ('CIV01', 'CIVIL', 'Anita Desai', 'Female', '1983-10-05'),
            ('CIV02', 'CIVIL', 'Mohan Kulkarni', 'Male', '1985-05-30'),
        ]
        for tid, dept_id, name, sex, dob in teacher_specs:
            first = name.split()[0].lower()
            username = '%s_%s' % (first, tid.lower())
            password = '%s_%s' % (first, dob[:4])
            user = make_user(username, password, name.split()[0], ' '.join(name.split()[1:]))
            teachers[tid], _ = Teacher.objects.update_or_create(
                id=tid,
                defaults={'user': user, 'dept': depts[dept_id], 'name': name, 'sex': sex, 'DOB': dob},
            )
        self.stdout.write('  [OK] %d faculty created' % len(teachers))

        # ---------- Students (4 named + 50 generated) ----------
        students = {}
        student_specs = [
            ('1BY21CS001', 'CS3A', 'Rahul Sharma', 'Male', '2004-01-15'),
            ('1BY21CS002', 'CS3A', 'Sneha Patil', 'Female', '2004-02-20'),
            ('1BY20CS003', 'CS5A', 'Arjun Mehta', 'Male', '2003-06-10'),
            ('1BY21EC001', 'EC3A', 'Priyanka Iyer', 'Female', '2004-09-12'),
        ]

        first_names = ['Aarav', 'Diya', 'Vivaan', 'Ananya', 'Advik', 'Ishaan', 'Myra', 'Kabir',
                       'Anika', 'Reyansh', 'Ishita', 'Aryan', 'Saanvi', 'Dev', 'Navya', 'Vihaan',
                       'Anaya', 'Rudra', 'Kiara', 'Atharv', 'Sara', 'Yash', 'Tara', 'Rohan', 'Zara',
                       'Manav', 'Ira', 'Krishna', 'Nisha', 'Veer', 'Shreya', 'Arnav', 'Riya', 'Dhruv',
                       'Pooja', 'Neil', 'Tanvi', 'Om', 'Simran', 'Harsh', 'Maya', 'Aditya', 'Gauri',
                       'Pranav', 'Jhanvi', 'Karan', 'Lakshmi', 'Nikhil', 'Ritika', 'Kunal']
        last_names = ['Sharma', 'Patel', 'Iyer', 'Reddy', 'Kulkarni', 'Mehta', 'Desai', 'Joshi',
                      'Nair', 'Rao', 'Verma', 'Singh', 'Gupta', 'Khan', 'Pillai', 'Chauhan', 'Bose',
                      'Acharya', 'Menon', 'Kapoor', 'Mishra', 'Das', 'Banerjee', 'Pandey', 'Tiwari',
                      'Naik', 'Hegde', 'Saxena', 'Trivedi', 'Bhatt']

        # build USN lists for extra students
        extra_usns = []
        for i in range(3, 16):
            extra_usns.append(('CS3A', '1BY21CS%03d' % i))
        for i in range(4, 25):
            extra_usns.append(('CS5A', '1BY20CS%03d' % i))
        for i in range(2, 9):
            extra_usns.append(('EC3A', '1BY21EC%03d' % i))
        for i in range(1, 7):
            extra_usns.append(('ME3A', '1BY21ME%03d' % i))
        for i in range(1, 4):
            extra_usns.append(('CIV3A', '1BY21CV%03d' % i))

        for idx, (cid, usn) in enumerate(extra_usns):
            first = first_names[idx % len(first_names)]
            last = last_names[(idx * 7 + 3) % len(last_names)]
            year = 2002 + (idx % 4)
            month = 1 + (idx % 12)
            day = 1 + (idx % 27)
            dob = '%04d-%02d-%02d' % (year, month, day)
            sex = 'Female' if idx % 2 else 'Male'
            student_specs.append((usn, cid, '%s %s' % (first, last), sex, dob))

        # delete stale demo students left over from older seed versions so the
        # final dataset matches the spec exactly
        wanted_usns = set(usn for usn, cid, name, sex, dob in student_specs)
        stale = Student.objects.exclude(USN__in=wanted_usns)
        stale_count = stale.count()
        stale.delete()

        for usn, cid, name, sex, dob in student_specs:
            first = name.split()[0].lower()
            username = '%s_%s' % (first, usn[-3:])
            password = '%s_%s' % (first, dob[:4])
            user = make_user(username, password, name.split()[0], ' '.join(name.split()[1:]))
            students[usn], _ = Student.objects.update_or_create(
                USN=usn,
                defaults={'user': user, 'class_id': classes[cid], 'name': name, 'sex': sex, 'DOB': dob},
            )
        self.stdout.write('  [OK] %d students created' % len(students))

        # ---------- Attendance range (before AssignTime so signal can build classes) ----------
        ar = AttendanceRange.objects.all().first()
        if ar is None:
            AttendanceRange.objects.create(
                start_date=date.today() - timedelta(days=70),
                end_date=date.today() + timedelta(days=30),
            )
        self.stdout.write('  [OK] Attendance date range set')

        # ---------- Assignments (course -> class -> teacher) ----------
        assign_specs = [
            ('CS3A', 'CS302', 'CS01'),
            ('CS3A', 'CS303', 'CS02'),
            ('CS3A', 'CS301', 'CS03'),
            ('CS3A', 'CS304', 'CS06'),
            ('CS5A', 'CS501', 'CS02'),
            ('CS5A', 'CS502', 'CS01'),
            ('CS5A', 'CS503', 'CS03'),
            ('CS5A', 'CS504', 'CS04'),
            ('CS5A', 'CS505', 'CS05'),
            ('EC3A', 'EC301', 'EC01'),
            ('EC3A', 'EC302', 'EC02'),
            ('EC3A', 'EC303', 'EC03'),
            ('ME3A', 'ME301', 'ME01'),
            ('ME3A', 'ME302', 'ME02'),
            ('CIV3A', 'CIV301', 'CIV01'),
            ('CIV3A', 'CIV302', 'CIV02'),
        ]
        assigns = []
        for cid, course_id, tid in assign_specs:
            ass, created = Assign.objects.get_or_create(
                class_id=classes[cid], course=courses[course_id], teacher=teachers[tid])
            assigns.append(ass)
        self.stdout.write('  [OK] %d course assignments created' % len(assigns))

        # ---------- Timetable (AssignTime) ----------
        tt_specs = [
            (assigns[0], [('Monday', '9:30 - 10:30'), ('Wednesday', '11:00 - 11:50')]),   # CS302 CS01
            (assigns[1], [('Tuesday', '7:30 - 8:30'), ('Thursday', '2:30 - 3:30')]),       # CS303 CS02
            (assigns[2], [('Friday', '7:30 - 8:30'), ('Friday', '8:30 - 9:30')]),          # CS301 CS03
            (assigns[3], [('Wednesday', '9:30 - 10:30'), ('Friday', '2:30 - 3:30')]),      # CS304 CS06
            (assigns[4], [('Monday', '7:30 - 8:30'), ('Wednesday', '2:30 - 3:30')]),       # CS501 CS02
            (assigns[5], [('Tuesday', '9:30 - 10:30'), ('Thursday', '11:00 - 11:50')]),    # CS502 CS01
            (assigns[6], [('Monday', '11:00 - 11:50'), ('Wednesday', '7:30 - 8:30')]),     # CS503 CS03
            (assigns[7], [('Monday', '8:30 - 9:30'), ('Thursday', '7:30 - 8:30')]),        # CS504 CS04
            (assigns[8], [('Tuesday', '11:00 - 11:50'), ('Friday', '9:30 - 10:30')]),      # CS505 CS05
            (assigns[9], [('Tuesday', '8:30 - 9:30'), ('Thursday', '9:30 - 10:30')]),      # EC301 EC01
            (assigns[10], [('Wednesday', '8:30 - 9:30'), ('Friday', '11:00 - 11:50')]),    # EC302 EC02
            (assigns[11], [('Monday', '11:50 - 12:40'), ('Thursday', '11:50 - 12:40')]),   # EC303 EC03
            (assigns[12], [('Monday', '2:30 - 3:30'), ('Wednesday', '11:50 - 12:40')]),    # ME301 ME01
            (assigns[13], [('Tuesday', '2:30 - 3:30'), ('Thursday', '8:30 - 9:30')]),      # ME302 ME02
            (assigns[14], [('Wednesday', '2:30 - 3:30'), ('Friday', '11:50 - 12:40')]),    # CIV301 CIV01
            (assigns[15], [('Tuesday', '9:30 - 10:30'), ('Thursday', '11:50 - 12:40')]),   # CIV302 CIV02
        ]
        for ass, slots in tt_specs:
            for day, slot in slots:
                AssignTime.objects.get_or_create(assign=ass, period=slot, day=day)
        self.stdout.write('  [OK] Timetable generated')

        # ---------- Demo attendance records ----------
        if not options['no_attendance']:
            marked = 0
            for ass in assigns:
                for att_class in AttendanceClass.objects.filter(assign=ass):
                    for stud in ass.class_id.student_set.all():
                        present = random.random() < 0.85
                        Attendance.objects.get_or_create(
                            course=ass.course, student=stud, attendanceclass=att_class,
                            date=att_class.date,
                            defaults={'status': present},
                        )
                        marked += 1
            self.stdout.write('  [OK] %d demo attendance records created' % marked)

        # Ensure AttendanceTotal rows exist for every student-course
        totals = 0
        for stud in Student.objects.all():
            for ass in stud.class_id.assign_set.all():
                StudentCourse.objects.get_or_create(student=stud, course=ass.course)
                AttendanceTotal.objects.get_or_create(student=stud, course=ass.course)
                totals += 1
        self.stdout.write('  [OK] Attendance totals synced')

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!\n'))
        self.stdout.write('Admin login : admin / Hitman@4165')
        self.stdout.write('Student login: rahul_001 / rahul_2004')
        self.stdout.write('Faculty login: anil_cs01 / anil_1980')
