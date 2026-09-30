from django.urls import path

from assignments import views

app_name = 'assignments'

urlpatterns = [
    path('', views.teacher_assignment_list, name='teacher_list'),
    path('add/', views.assignment_create, name='create'),
    path('<int:pk>/edit/', views.assignment_edit, name='edit'),
    path('<int:pk>/delete/', views.assignment_delete, name='delete'),
    path('<int:pk>/submissions/', views.assignment_submissions, name='submissions'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade'),

    path('mine/', views.student_assignment_list, name='student_list'),
    path('<int:pk>/submit/', views.assignment_submit, name='submit'),
]
