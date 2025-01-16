from typing import Union, Optional

from pydantic import Field, BaseModel
from typing_extensions import TypedDict


class Speaker(BaseModel):
    name: str = Field(description="发言者姓名")
    gender: str = Field(default=None, description="性别")
    # emotion: Literal['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral'] = Field(default=Emotion.neutral, description="发言情绪")


class Answer(BaseModel):
    answer: list[str]


class Analysis(BaseModel):
    answer: str = Field(description="试题的正确选项")
    analysis: str = Field(description="试题的中文分析")


class Material(BaseModel):
    speaker: Speaker
    content: str


class modify_question(BaseModel):
    material: Optional[str] = Field(default=None, description="试题的素材或资料")
    question_and_answer: list[dict] = Field(description="试题的问题和选项")
    answer: Answer = Field(description="试题的答案")
    analysis: list = Field(description="试题的中文分析")


class QuestionAndOptions(BaseModel):
    question: str = Field(description="试题的问题")
    options: list[dict] = Field(description="试题的选项")


class BaseQuestion(BaseModel):
    """A question and its options."""

    question_and_options: list[QuestionAndOptions] = Field(description="试题的问题和选项")
    answer: Answer = Field(description="试题的答案列表")
    analysis: list[Analysis] = Field(description="试题的中文分析")


class ListeningMaterial(BaseModel):
    material: list[Material] = Field(default=None, description="对话素材")


class ListeningQuestion(BaseModel):
    final_output: Union[BaseQuestion, ListeningMaterial]


class Translation(BaseModel):
    translation: list[Material] = Field(default=None, description="翻译以后的对话素材")


class ConversationalResponse(BaseModel):
    """Respond in a conversational manner. Be kind and helpful."""

    response: str = Field(description="A conversational response to the user's query")


class ToolResponse(BaseModel):
    """Respond in a conversational manner. Be kind and helpful."""
    ToolResponse: str = Field(description="A conversational response from tools")
    response: str = Field(description="A conversational response to the user's query")


class response(BaseModel):
    final_output: Union[ListeningQuestion, modify_question, ConversationalResponse, ToolResponse]
