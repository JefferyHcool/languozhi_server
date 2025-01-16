# Import relevant functionality
import os
from enum import Enum
from typing import Optional, Union, Type, Literal

import requests
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.tools import BaseTool, StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAI
from pydantic import BaseModel, Field

from languozhi_core import Classification
from languozhi_core.function_call.functions import listening_material_prompts
from languozhi_core.prompts import BASE_PROMPT, listening_template


# Create the agent

def search(query: str) -> str:
    """Search the web for information and return a summary."""
    return '黄建武是男生'


class Emotion(Enum):
    happy = 'happy'
    sad = 'sad'
    angry = 'angry'
    surprise = 'surprise'
    fear = 'fear'
    disgust = 'disgust'
    neutral = 'neutral'


class Speaker(BaseModel):
    name: str = Field(description="发言者姓名")
    gender: str = Field(default=None, description="性别")
    # emotion: Literal['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral'] = Field(default=Emotion.neutral, description="发言情绪")


class Material(BaseModel):
    speaker: Speaker
    content: str


class modify_question(BaseModel):
    material: Optional[str] = Field(default=None, description="试题的素材或资料")
    question_and_answer: list[dict] = Field(description="试题的问题和选项")
    answer: list = Field(description="试题的答案")
    analysis: list = Field(description="试题的中文分析")


class QuestionAndOptions(BaseModel):
    question: str = Field(description="试题的问题")
    options: list[dict] = Field(description="试题的选项")


class BaseQuestion(BaseModel):
    """A question and its options."""

    question_and_options: list[QuestionAndOptions] = Field(description="试题的问题和选项")
    answer: list = Field(description="试题的答案")
    analysis: list = Field(description="试题的中文分析")


class ListeningMaterial(BaseModel):
    material: list[Material] = Field(default=None, description="对话素材")


class ListeningQuestion(BaseModel):
    final_output: Union[BaseQuestion, ListeningMaterial]


class ConversationalResponse(BaseModel):
    """Respond in a conversational manner. Be kind and helpful."""

    response: str = Field(description="A conversational response to the user's query")


class ToolResponse(BaseModel):
    """Respond in a conversational manner. Be kind and helpful."""
    ToolResponse: str = Field(description="A conversational response from tools")
    response: str = Field(description="A conversational response to the user's query")


class response(BaseModel):
    final_output: Union[ListeningQuestion, modify_question, ConversationalResponse, ToolResponse]


def search_weather(query: str) -> str:
    """Search the web for information and return a summary."""
    key = '0de56eca427701976cd0930b0390efa6'
    parameters = {
        'key': key,
        'city': query,
    }
    url = 'https://restapi.amap.com/v3/weather/weatherInfo?parameters'
    res = requests.get(url, parameters)
    return res.text


load_dotenv()
memory = MemorySaver()


# model = ChatOpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url=os.getenv('DEEPSEEK_BASE_URL'),
#                    model='deepseek-chat')
# llm = ChatOpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url=os.getenv('DEEPSEEK_BASE_URL'),
#                  model='deepseek-chat')
# print(llm.invoke('你好'))

# tools = [StructuredTool.from_function(
#     func=search_weather,
#     name="search_weather",  # fixed
#     description="查询天气",
#     parse_docstring=True,
# )]
#
# prompt_template='生成一道英语 {kind} 题，难度是{difficulty} ，题目数量是{counts} '
# prompt=ChatPromptTemplate.from_template(prompt_template)
# structured_llm =llm.with_structured_output(response)
# llm = llm.bind_tools(tools)
#
# chain=prompt | llm | structured_llm
# result=chain.invoke({'kind':'听力','difficulty':'简单','counts':'5'})
# print(result)
# #

# llm_with_tool=llm.bind_tools(tools)
# structured_llm = llm.with_structured_output(response)
# data =  llm_with_tool.invoke("今天昆明天气怎么样")
# chain= structured_llm | tools
# data = chain.invoke({"messages": [HumanMessage(content="今天昆明天气怎么样")]})
# print(data)


# print(data.material, end='\n')
# print(data.question_and_options, end='\n')
# print(data.answer, end='\n')
# print(data.analysis, end='\n')
#
# tools = [StructuredTool.from_function(
#     func=search_weather,
#     name="search_weather",  # fixed
#     description="查询天气",
#     parse_docstring=True,
# )]
# agent_executor = create_react_agent(model, tools, checkpointer=memory)
#
# # Use the agent
# config = {"configurable": {"thread_id": "abc123"}}
# for chunk in agent_executor.stream(
#         {"messages": [HumanMessage(content="你好 我是jeff 我住在昆明")]}, config
# ):
#     print(chunk)
#     print("----")
# for chunk in agent_executor.stream(
#         {"messages": [HumanMessage(content="今天我是否应该带雨伞")]}, config
# ):
#     print(chunk)
#     print("----")


class Questioner:
    def __init__(self, llm: ChatOpenAI, classification: str, difficulty: str, count: int, questions_per_item: int,
                 topic: Optional[str] = None,
                 extra: Optional[str] = None):
        '''
        :param llm: 大模型
        :param classification: 题目类型
        :param difficulty: 题目难度
        :param count: 题目数量
        :param questions_per_item: 题目数量
        :param topic: 题目主题
        :param extra: 额外的资料
        '''
        self.llm = llm
        self.classification = classification
        self.difficulty = difficulty
        self.count = count
        self.questions_per_item = questions_per_item
        self.topic = topic
        self.extra = extra
        self.base_prompt = BASE_PROMPT
        self._formatter = None

    def listening_question(self, args) -> ListeningQuestion:
        materials = args.get('materials', {})
        self.base_prompt = BASE_PROMPT
        materials_obj = {
            'str_content': '',
            'raw_content': ''
        }
        material_prompt = listening_material_prompts(
            _format=materials.get('_format', None),
            topic=materials.get('topic', None),
            scene=materials.get('scene', None),
            participants=materials.get('participants', None),
            level=materials.get('level', None),
            length=materials.get('length', None),
            details=materials.get('details', None)
        )
        self._formatter = ListeningQuestion
        llm = self.llm.with_structured_output(self._formatter)

        # 定义生成听力素材的 prompt
        _prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.base_prompt),
                ("human", material_prompt)
            ]
        )

        # 定义生成听力题目的 prompt
        _question_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", listening_template),
            ]
        )

        # 生成听力素材的 chain
        material_prompt = RunnableLambda(
            lambda x: _prompt.format_prompt(**x.get('materials'))
        )

        # 生成听力题目的 chain
        question_prompt = RunnableLambda(
            lambda x: _question_prompt.format_prompt(**x)
        )

        # 调用 LLM 生成听力素材
        material_generator = RunnableLambda(
            lambda x: llm.invoke(x.to_messages())
        )

        def _generate_question(template):
            print('template', template.to_messages())
            return llm.invoke(template.to_messages())

        # 调用 LLM 生成听力题目
        _generator_q = RunnableLambda(
            lambda x: _generate_question(x)
        )

        def set_material(material_result):

            materials_obj['raw_content'] = material_result.final_output
            for i in material_result.final_output.material:
                materials_obj['str_content'] += i.speaker.name + ':' + i.content

        # 定义一个函数，将生成的听力素材和原始参数合并
        def combine_material_and_args(material_result):
            print('material_result', material_result)
            self._formatter = BaseQuestion
            set_material(material_result)
            return {
                'material': materials_obj['str_content'],
                'classification': args.get('classification', None),
                'difficulty': args.get('difficulty', None),
                'questions_per_item': args.get('questions_per_item', 3),
            }

        # 将 combine_material_and_args 包装成 Runnable
        combine_runnable = RunnableLambda(
            lambda x: combine_material_and_args(x)
        )

        # 构建完整的 chain
        chain = RunnableSequence(
            first=material_prompt,
            middle=[material_generator],
            last=RunnableSequence(
                first=combine_runnable,
                middle=[question_prompt],
                last=_generator_q
            )
        )

        materials_res = chain.invoke({
            'materials': {
                "_format": materials.get('_format', None),
                "count": args.get('count', 1),
                "scene": materials.get('scene', None),
                "participants": materials.get('participants', None),
                "level": materials.get('level', None),
                "length": materials.get('length', None),
                "details": materials.get('details', None),
                "topic": materials.get('topic', None),
            }
        })
        model = self.llm.with_structured_output(BaseQuestion)
        chain2 = RunnableSequence(
            first=question_prompt,
            last=_generator_q
        )
        res = chain2.invoke(
            {combine_material_and_args(materials_res)}
        )
        # 调用 chain 生成听力素材和题目

        print(res)

        for i in res.ListeningMaterial.material:
            print(i.speaker.name + '::' + i.content)

        return res

    def generate_message(self):
        print(self.classification)

        if self.classification == Classification.LISTENING.value:
            self._formatter = ListeningQuestion
            if not self.topic:
                prompt_template = ''

            else:
                prompt_template = ''
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.base_prompt),
                    ("human", prompt_template)
                ]
            )
            return prompt

    def get_formatter(self) -> BaseModel:
        return self._formatter()

    @staticmethod
    def print_formatter(response: dict) -> None:
        """
        :param response: 响应
        """

    @staticmethod
    def print_question_data(question_data: ListeningQuestion):
        # 打印 material
        print(question_data)
        print("Materials:")
        for idx, mat in enumerate(question_data.material or []):
            print(f"{mat.speaker}: {mat.content}")

        # 打印 question_and_options
        print("\nQuestions and Options:")
        for idx, question in enumerate(question_data.question_and_options):
            print(f"  Question {idx + 1}: {question.get('question')}")
            for option_key, option_value in question.get('options', {}).items():
                print(f"    {option_key}: {option_value}")

        # 打印 answer
        print("\nAnswers:")
        for idx, ans in enumerate(question_data.answer):
            print(f"  Answer {idx + 1}: {ans}")

        # 打印 analysis
        print("\nAnalysis:")
        for idx, ana in enumerate(question_data.analysis):
            print(f"  Analysis {idx + 1}: {ana}")

    def generate_question(self):
        prompt = self.generate_message()
        self.llm = self.llm.with_structured_output(self._formatter)
        chain = prompt | self.llm

        raw_output = chain.invoke({
            'classification': self.classification,
            'difficulty': self.difficulty,
            'count': self.count,
            'questions_per_item': self.questions_per_item,
            'topic': self.topic,
            'extra': self.extra

        })

        return raw_output
