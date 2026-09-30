from django.urls import path

from chat import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('find/', views.find_students, name='find_students'),
    path('requests/', views.friend_requests, name='friend_requests'),
    path('requests/send/<int:user_id>/', views.send_friend_request, name='send_request'),
    path('requests/<int:pk>/<str:action>/', views.respond_friend_request, name='respond_request'),
    path('with/<int:user_id>/', views.conversation, name='conversation'),
    path('with/<int:user_id>/poll/', views.poll_messages, name='poll_messages'),
]
