from django.urls import path
from .views import ChatbotView

app_name = 'psassist'

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chat-endpoint'),
]

