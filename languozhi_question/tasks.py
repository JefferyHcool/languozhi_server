from celery import shared_task

from languozhi_question.services.question_service import QuestionServices


@shared_task
def generate_questions_task(payload):
    print("generate_questions_task")
    QS = QuestionServices()
    return QS.generate_questions(payload)
