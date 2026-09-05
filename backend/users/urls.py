from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('chat/', views.chat_command, name='chat_command'),
]