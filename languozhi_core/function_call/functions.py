from typing import Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from languozhi_core.prompts import dialogue_template, dialogue_template_scene, dialogue_template_participants, \
    dialogue_template_level, dialogue_template_length, dialogue_template_details, dialogue_template_topic
from langchain.prompts import ChatPromptTemplate


# class ListeningMaterials(BaseModel):
#     _format: Optional[str] = Field(..., default="对话", description="对话类型（长对话，短对话，独白）")
#     scene: Optional[str] = Field(..., default="大模型随机发挥可不传", description="对话场景")
#     participants: Optional[str] = Field(..., default="大模型随机发挥可不传", description="对话人物")
#     level: Optional[str] = Field(..., default="大模型随机发挥可不传", description="对话难度")
#     length: Optional[str] = Field(..., default="大模型随机发挥可不传", description="对话长度")
#     details: Optional[str] = Field(..., default=None, description="对话需要的细节用户会传入")
#
#
# class ListeningMaterialPromptGenerator(BaseTool):
#     name: str = "ListeningMaterialPromptGenerator"
#     description: str = "Generate a prompt for listening material."
#     args_schema: Type[BaseModel] = ListeningMaterials
#     return_direct: bool = False
#
#     def _run(self, _format: str, scene: Optional[str] = None, participants: Optional[str] = None,
#              level: Optional[str] = None,
#              length: Optional[str] = None, details: Optional[str] = None):
#         base_prompt = dialogue_template
#         if scene:
#             base_prompt += dialogue_template_scene
#         if participants:
#             base_prompt += dialogue_template_participants
#
#         if level:
#             base_prompt += dialogue_template_level
#
#         if length:
#             base_prompt += dialogue_template_length
#
#         if details:
#             base_prompt += dialogue_template_details
#
#         return base_prompt
#

def listening_material_prompts(_format:  Optional[str] = '对话', count:Optional[int]=1, scene: Optional[str] = None, participants: Optional[str] = None,
                               level: Optional[str] = None,topic: Optional[str] = None,
                               length: Optional[str] = None, details: Optional[str] = None):
    base_prompt = dialogue_template
    if scene:
        base_prompt += dialogue_template_scene
    if participants:
        base_prompt += dialogue_template_participants
    if topic:
        base_prompt +=  dialogue_template_topic
    if level:
        base_prompt += dialogue_template_level

    if length:
        base_prompt += dialogue_template_length

    if details:
        base_prompt += dialogue_template_details

    return base_prompt
