from django.urls import path, include

from .views import *

urlpatterns = [
    # ----------------------- SEASONS URL'S -----------------------
    path('season/<int:user_id>', StudentSeasonsAPIView.as_view(), name='student-seasons'),
    path('season/course/<int:user_id>', StudentCoursesAPIView.as_view(), name='student-courses'),
    path('season/list/<int:user>', SeasonListAPIView.as_view(), name='season-list'),
    
    # ----------------------- MEMBERS URL'S -----------------------
    path('members/list', MemberListAPIView.as_view(), name='member-list'),
    path('members/create', MemberCreateAPIView.as_view(), name='member-create'),
    
    # ----------------------- COURSES URL'S -----------------------
    path('courses/list', CourseListAPIView.as_view(), name='course-list'),
    path('courses/create', StudentCreateDeclarativaAPIView.as_view(), name='season-course-create'),

    # ----------------------- STUDENT URL'S -----------------------
    path('teacher/list/<int:teacher>', TeacherListView.as_view(), name='teacher-list'),
    path('student/update/<int:pk>', StudentUpdateView.as_view(), name='update-student'),
    path('student/list', StudentListAPIView.as_view(), name='student-list'),
    path('student/create', StudentCreateAPIView.as_view(), name='student-create'),
    path('student/declarativa', StudentCreateDeclarativaAPIView.as_view(), name='student-declarativa'),
    
    # ----------------------- LOGIN URL'S -----------------------
    path('login/<str:dni>', LoginAPIView.as_view(), name='login'),

    # ----------------------- VOUCHER URL'S -----------------------
    path('vouchers/create', VoucherCreateAPIView.as_view(), name='voucher-create'),
    path('vouchers/list', VoucherListAPIView.as_view(), name='voucher-list'),
    path('vouchers/detail/<int:pk>', VoucherDetailAPIView.as_view(), name='voucher-detail'),
    path('vouchers/image/<int:voucher_id>', voucher_image_view, name='voucher-image'),
]
