from rest_framework import serializers

from info.models import AttendanceTotal, StudentCourse, Marks, AssignTime, Student


class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_id = serializers.CharField(source='course.id', read_only=True)
    attended = serializers.IntegerField(source='att_class', read_only=True)
    total = serializers.IntegerField(source='total_class', read_only=True)
    percentage = serializers.FloatField(source='attendance', read_only=True)

    class Meta:
        model = AttendanceTotal
        fields = ('course_id', 'course_name', 'attended', 'total', 'percentage')


class MarksSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_usn = serializers.CharField(source='student.USN', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_shortname = serializers.CharField(source='course.shortname', read_only=True)
    tests = serializers.SerializerMethodField()

    class Meta:
        model = StudentCourse
        fields = ('student_name', 'student_usn', 'course_name', 'course_shortname', 'tests')

    def get_tests(self, obj):
        return [
            {'name': m.name, 'marks': m.marks1, 'total': m.total_marks}
            for m in obj.marks_set.all()
        ]


class TimeTableSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='assign.course.shortname', read_only=True)
    class_id = serializers.CharField(source='assign.class_id.id', read_only=True)

    class Meta:
        model = AssignTime
        fields = ('class_id', 'course', 'day', 'period')
