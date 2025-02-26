from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from enums.http_code_enums import ResponseCode
from languozhi_core import LLMEnum, ModelType
from languozhi_core.core import LanguozhiCore
from languozhi_question.services.question_service import QuestionServices
from utils.response import ApiResponse


# Create your views here.

from .tasks import generate_questions_task
from celery.result import AsyncResult

class QuestionGenerationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            payload = request.data
            task = generate_questions_task.delay(payload)  # 异步执行
            return ApiResponse.success(data={"task_id": task.id}, msg="任务已提交", code=ResponseCode.SUCCESS)
        except Exception as e:
            return ApiResponse.error(msg=str(e), code=ResponseCode.ERROR)

class QuestionGenerationStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        result = AsyncResult(task_id)
        if result.state == "PENDING":
            return ApiResponse.success(data={"status": "进行中"}, msg="任务进行中", code=ResponseCode.SUCCESS)
        elif result.state == "SUCCESS":
            return ApiResponse.success(data={"status": "完成", "result": result.result}, msg="任务完成", code=ResponseCode.SUCCESS)
        else:
            return ApiResponse.error(msg="任务失败", code=ResponseCode.ERROR)
