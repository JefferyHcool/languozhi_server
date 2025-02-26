from languozhi_core import LLMEnum, ModelType
from languozhi_core.core import LanguozhiCore


class QuestionServices:
    def __init__(self):
        pass

    def generate_questions(self, payload):
        '''

        :param payload: {
    "id": "hgqat1tnDvXMFlZkXABZZ",
    "classification": "listening",
    "data": {
        "classification": "听力",
        "difficulty": "elementary",
        "materials": [
            {
                "_format": "对话",
                "topic": "AI焦虑",
                "participants": "3"
            }
        ]
    }
}
        :return:
        '''
        try:
            core = LanguozhiCore(LLMEnum.DEEPSEEK, ModelType.DEEP_CHAT)
            print(payload)
            payload = payload.get('data')

            for i in payload.get('materials'):
                args = {
                    "classification": payload.get('classification'),
                    "difficulty": payload.get('difficulty'),
                    "count": payload.get('count'),
                    "questions_per_item": payload.get('questions_per_item'),
                    "extra": payload.get('extra'),
                    "materials": i,
                }
                result = core.send_requirement(args=args)
            return result
        except Exception as e:
            print(e)
