from django.urls import path

from attendance import views

app_name = 'attendance'

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark'),
    path('bulk-upload/', views.bulk_upload_attendance, name='bulk_upload'),
    path('template.csv', views.attendance_csv_template, name='csv_template'),

    path('mine/', views.student_attendance, name='student_view'),

    path('overview/', views.admin_attendance_overview, name='admin_overview'),
]
