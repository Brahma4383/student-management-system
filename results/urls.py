from django.urls import path

from results import views

app_name = 'results'

urlpatterns = [
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/add/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/edit/', views.exam_edit, name='exam_edit'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('overview/', views.admin_results_overview, name='admin_overview'),

    path('entry/', views.enter_results, name='entry'),

    path('mine/', views.student_results, name='student_results'),
]
