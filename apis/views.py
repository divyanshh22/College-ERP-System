from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from info.models import Student, Teacher, AttendanceTotal, StudentCourse, AssignTime
from .serializers import (
    DetailSerializer,
    AttendanceSerializer,
    MarksSerializer,
    TimeTableSerializer,
)


# =========================
# STUDENT / TEACHER DETAIL API
# =========================
class DetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DetailSerializer

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        if hasattr(request.user, 'student'):
            serializer = DetailSerializer(request.user.student)
        elif hasattr(request.user, 'teacher'):
            serializer = DetailSerializer(request.user.teacher)
        else:
            return Response({'role': 'admin', 'username': request.user.username})
        return Response(serializer.data)


# =========================
# ATTENDANCE API
# =========================
class AttendanceView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return AttendanceTotal.objects.filter(student=self.request.user.student)
        if hasattr(self.request.user, 'teacher'):
            teacher = self.request.user.teacher
            return AttendanceTotal.objects.filter(course__assign__teacher=teacher)
        return AttendanceTotal.objects.none()


# =========================
# MARKS API
# =========================
class MarksView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MarksSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return StudentCourse.objects.filter(student=self.request.user.student)
        if hasattr(self.request.user, 'teacher'):
            teacher = self.request.user.teacher
            return StudentCourse.objects.filter(course__assign__teacher=teacher)
        return StudentCourse.objects.none()


# =========================
# TIMETABLE API
# =========================
class TimetableView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TimeTableSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return AssignTime.objects.filter(assign__class_id=self.request.user.student.class_id)
        if hasattr(self.request.user, 'teacher'):
            return AssignTime.objects.filter(assign__teacher=self.request.user.teacher)
        return AssignTime.objects.none()


# =========================
# LOGIN API (returns auth token)
# =========================
class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'role': 'student' if hasattr(user, 'student')
                        else 'teacher' if hasattr(user, 'teacher') else 'admin',
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


# =========================
# LOGOUT VIEW (FINAL FIX)
# =========================
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
