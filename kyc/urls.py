# urls.py
from django.urls import path
from .views import CreateSessionView, SessionResultView

urlpatterns = [
    path('create-session/', CreateSessionView.as_view()),
    path('session-result/', SessionResultView.as_view()),
]