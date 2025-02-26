import os
import logging
from typing import Dict, Any, TypedDict, Optional

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from languozhi_core import LLMEnum, ModelType
from languozhi_core.agents.ListeningQuestion import ListeningQuestionGenerator
from languozhi_core.prompts import BASE_PROMPT

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuestionArgs(TypedDict):
    classification: str
    difficulty: str
    count: str
    questions_per_item: str
    extra: Optional[str]
    materials: Dict[str, str]


class LanguozhiCore:
    def __init__(self, LLM: LLMEnum, model_name: ModelType):
        logger.info(f"初始化 LanguozhiCore，LLM: {LLM.value}, 模型: {model_name.value}")
        self._load_env_vars(LLM)
        self.llm = self._initialize_llm(LLM, model_name)
        self.model_name = model_name
        self.args = {}
        self.file_path = os.getenv('FILE_PATH')

    def _load_env_vars(self, LLM: LLMEnum) -> None:
        """加载环境变量"""
        self.api_key = os.getenv(f'{LLM.value}_API_KEY')
        self.base_url = os.getenv(f'{LLM.value}_BASE_URL')
        if not self.api_key or not self.base_url:
            raise ValueError(f"未找到 {LLM} 的环境变量配置")

    def _initialize_llm(self, LLM: LLMEnum, model_name: ModelType) -> ChatOpenAI:
        """初始化 LLM"""
        if LLM == LLMEnum.OPENAI or LLM == LLMEnum.DEEPSEEK:
            return ChatOpenAI(
                api_key=os.getenv(f'{LLM.value}_API_KEY'),
                base_url=os.getenv(f'{LLM.value}_BASE_URL'),
                model=f'{model_name.value}',
                temperature=0.2,
            )
        else:
            raise ValueError(f"不支持的 LLM: {LLM}")

    def parsing_args(self, args: QuestionArgs) -> None:

        """解析参数并存储到实例变量中"""
        try:
            #dict 转为 QuestionArgs
            args = QuestionArgs(**args)
            self.args = {
                'classification': args.get('classification'),
                'difficulty': args.get('difficulty'),
                'count': args.get('count'),
                'questions_per_item': args.get('questions_per_item'),
                'topic': args.get('topic'),
                'extra': args.get('extra'),
            }

        except Exception as e:
            logger.error(f"解析参数时发生错误: {e}")
            raise

    def generate_executor(self) -> Any:
        """动态生成执行器"""
        executor_map = {
            '听力': ListeningQuestionGenerator,
            # '阅读': ReadingQuestionGenerator,  # 未来扩展
        }
        executor_class = executor_map.get(self.args['classification'])
        if not executor_class:
            raise ValueError(f"未知的分类: {self.args['classification']}")
        return executor_class(self.llm, base_prompt=BASE_PROMPT)

    def send_requirement(self, args: QuestionArgs) -> Any:
        """发送需求并生成问题"""
        try:
            self.parsing_args(args)
            executor = self.generate_executor()
            method_map = {
                '听力': 'listening_question',
                # '阅读': 'reading_question',  # 未来扩展
            }
            method_name = method_map.get(self.args['classification'])
            if not method_name:
                raise ValueError(f"未知的分类: {self.args['classification']}")

            return executor.start(args)
        except Exception as e:
            logger.error(f"生成问题时发生错误: {e}")
            raise


if __name__ == '__main__':
    core = LanguozhiCore(LLMEnum.DEEPSEEK, ModelType.DEEP_CHAT)
    # TODO 添加资料文件解析




    question = core.send_requirement(args=
    {
        "classification": "听力", 'difficulty': '小学三年级', "count": "2",
        "questions_per_item": "3",'extra':'',
        'materials': {
            '_format': '对话', 'scene': '', 'participants': '3', 'level': '小学三年级', 'length': '不低于10轮对话',
            'topic': '',
            'details': ''''''
        }
    }
    )
