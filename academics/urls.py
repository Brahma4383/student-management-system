from django.urls import path

from academics import views

app_name = 'academics'

urlpatterns = [
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.class_create, name='class_create'),
    path('classes/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),

    path('sections/add/', views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', views.section_edit, name='section_edit'),
    path('sections/<int:pk>/delete/', views.section_delete, name='section_delete'),

    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    path('teaching-assignments/', views.teaching_assignment_list, name='teaching_assignment_list'),
    path('teaching-assignments/add/', views.teaching_assignment_create, name='teaching_assignment_create'),
    path('teaching-assignments/<int:pk>/delete/', views.teaching_assignment_delete, name='teaching_assignment_delete'),
]
