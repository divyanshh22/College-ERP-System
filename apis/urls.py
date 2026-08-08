from django.urls import path
from apis.views import (
    DetailView,
    AttendanceView,
    MarksView,
    TimetableView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path('detail/', DetailView.as_view()),
    path('attendance/', AttendanceView.as_view()),
    path('marks/', MarksView.as_view()),
    path('timetable/', TimetableView.as_view()),
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
