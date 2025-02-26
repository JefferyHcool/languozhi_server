# users/urls.py
from django.urls import path

from languozhi_question.views import QuestionGenerationAPIView, QuestionGenerationStatusAPIView

urlpatterns = [
    path('generate/', QuestionGenerationAPIView.as_view(), name='question_generate'),
    path('status/<str:task_id>/', QuestionGenerationStatusAPIView.as_view(), name='question_status'),
]
