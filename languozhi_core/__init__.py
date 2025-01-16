import enum
from typing import List


# LLM models
class LLMEnum(enum.Enum):
    OPENAI = "OPENAI"
    DEEPSEEK = "DEEPSEEK"
    QWEN = "QWEN"


class Classification(enum.Enum):
    LISTENING = "听力"  # 听力
    WRITING = "写作"  # 写作
    READING_COMPREHENSION = "阅读理解"  # 阅读理解
    TRANSLATION = "翻译"  # 翻译
    CLOZE = '完形填空'
    SINGLE_CHOICE = "单选题"
    CORRECT_ESSAY = '短文改错'
    COMPLETE_SENTENCE = '补全对话'


class ModelType(enum.Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"
    GPT_4_TURBO = "gpt-4-turbo"
    DEEP_CHAT = 'deepseek-chat'
