from django.urls import path

from accounts import views
from accounts.models import User

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.RoleAwareLoginView.as_view(), name='login'),
    path('logout/', views.RoleAwareLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/password/', views.change_password_view, name='change_password'),

    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    path('admin-panel/teachers/', views.teacher_list, name='teacher_list'),
    path('admin-panel/teachers/add/', views.teacher_create, name='teacher_create'),
    path('admin-panel/teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('admin-panel/teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    path('admin-panel/teachers/<int:pk>/reset-password/', views.reset_password,
         {'role': User.Role.TEACHER}, name='teacher_reset_password'),

    path('admin-panel/students/', views.student_list, name='student_list'),
    path('admin-panel/students/add/', views.student_create, name='student_create'),
    path('admin-panel/students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('admin-panel/students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('admin-panel/students/<int:pk>/reset-password/', views.reset_password,
         {'role': User.Role.STUDENT}, name='student_reset_password'),
]
