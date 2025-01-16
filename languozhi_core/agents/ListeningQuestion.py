import uuid
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSequence, RunnableParallel

from languozhi_core.function_call.functions import listening_material_prompts
from languozhi_core.prompts import listening_template, translation_prompt
from languozhi_core.structure import ListeningQuestion, BaseQuestion, ListeningMaterial, Translation
from utils.cos import TencentCOSUploader
from utils.voice_generator import VoiceGenerator


class ListeningQuestionGenerator:
    def __init__(self, llm, base_prompt: str):
        self.llm = llm
        self.base_prompt = base_prompt
        self.materials_obj = {'str_content': '', 'raw_content': ''}
        self.generator = VoiceGenerator()
        self.file_name=uuid.uuid4().__str__().replace('-', '')+'.mp3'

    def count_validator(self, args: Dict[str, Any],count: int):
        if args.get('question_and_options'):
            if len(args.get('question_and_options')) < count:
                return False
        return True
    def _generate_material_prompt(self, materials: Dict[str, Any]) -> ChatPromptTemplate:
        """生成听力素材的 prompt"""
        material_prompt = listening_material_prompts(
            _format=materials.get('_format', None),
            topic=materials.get('topic', None),
            scene=materials.get('scene', None),
            participants=materials.get('participants', None),
            level=materials.get('level', None),
            length=materials.get('length', None),
            details=materials.get('details', None)
        )
        return ChatPromptTemplate.from_messages([
            ("system", self.base_prompt),
            ("human", material_prompt)
        ])

    def _generate_question_prompt(self) -> ChatPromptTemplate:
        """生成听力题目的 prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", self.base_prompt),
            ("human", listening_template),
        ])

    def _generate_translation_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.base_prompt),
            ("human", translation_prompt),
        ])

    def _generate_material(self, prompt: ChatPromptTemplate) -> Any:
        """调用 LLM 生成听力素材"""
        return self.llm.with_structured_output(ListeningQuestion).invoke(prompt.to_messages())

    def _generate_question(self, prompt: ChatPromptTemplate) -> Any:
        """调用 LLM 生成听力题目"""
        return self.llm.with_structured_output(BaseQuestion).invoke(prompt.to_messages())

    def _generate_translation(self, prompt: ChatPromptTemplate) -> Any:
        """调用 LLM 生成翻译"""
        return self.llm.with_structured_output(Translation).invoke(prompt.to_messages())

    def _set_material(self, material_result: Any) -> None:
        """设置听力素材内容"""
        self.materials_obj['raw_content'] = material_result.final_output
        self.materials_obj['str_content'] = ''.join(
            f"{i.speaker.name}:{i.content}" for i in material_result.final_output.material
        )

    def serialize_all(
            self, material_result: ListeningMaterial or str,
            question_result: BaseQuestion,
            translation: Translation) -> dict:
        obj = {'material': material_result.dict()['material'],
               'question_and_options': question_result.dict()['question_and_options'],
               'answer': question_result.dict()['answer'], 'analysis': question_result.dict()['analysis'],
               'translation': translation.dict()['translation'],
               }
        return obj

    @staticmethod
    def _print(data: dict):
        # 打印对话内容
        print("=== 对话内容 ===")
        for item in data['material']:
            speaker = item['speaker']['name']
            content = item['content']
            print(f"{speaker}: {content}")
        print()

        # 打印问题和选项
        print("=== 问题与选项 ===")
        for qa in data['question_and_options']:
            print(f"问题: {qa['question']}")
            for option in qa['options']:
                for key, value in option.items():
                    print(f"{key}: {value}")
        print()

        # 打印答案
        print("=== 答案 ===")
        answer = data['answer']['answer']
        print(f"答案: {', '.join(answer)}")
        print()

        # 打印分析
        print("=== 分析 ===")
        for analysis in data['analysis']:
            print(f"答案: {analysis['answer']}")
            print(f"分析: {analysis['analysis']}")

        print("=== 翻译 ===")
        for item in data['translation']:
            speaker = item['speaker']['name']
            content = item['content']
            print(f"{speaker}: {content}")
        print()

    def _combine_material_and_args(self, material_result: Any, args: Dict[str, Any]) -> Dict[str, Any]:
        """合并生成的听力素材和原始参数"""

        self._set_material(material_result)
        return {
            'material': self.materials_obj['str_content'],
            'classification': args.get('classification', None),
            'difficulty': args.get('difficulty', None),
            'questions_per_item': args.get('questions_per_item', 3),
        }

    def rec_speaker(self, material_result: Any):
        speaker_list = {}
        print('speaker_list', material_result)
        for i in material_result:
            name = i['speaker']['name']
            gender = i['speaker']['gender']
            if not speaker_list.get(name, None):
                speaker_list[name] = gender

        return speaker_list

    def voice_material(self, args: Dict[str, Any]) -> Any:

        speaker_list = self.rec_speaker(args.get('material'))
        speaker_model = []
        for i in speaker_list.keys():
            if speaker_list[i] == 'female':
                model=self.generator.filter_by_gender('f')
            else:
                model=self.generator.filter_by_gender('m')
            speaker_model.append({
                'speaker':i,
                'model':model['name']
            })
        for m in args.get('material'):
            speaker = m['speaker']['name']
            content = m['content']
            voice_model=''
            for i in speaker_model:
                if speaker == i['speaker']:
                    voice_model=i['model']
            path= self.generator.generate_voice(text=content,voice_model=voice_model,file_name=self.file_name)
            self.upload_material(path=path)


    def upload_material(self, path:str)->None:
        uploader = TencentCOSUploader()

        # 上传文件，不使用断点续传
        response = uploader.upload_file(
            key=self.file_name,
            local_file_path=path,
            enable_md5=True,
            progress_callback=None
        )

    def start(self, args: Dict[str, Any]) -> Dict:
        """生成听力题目"""
        materials = args.get('materials', {})
        material_prompt = self._generate_material_prompt(materials)
        question_prompt = self._generate_question_prompt()
        _translation_prompt = self._generate_translation_prompt()
        # 生成听力素材的 chain
        material_chain = RunnableSequence(
            first=RunnableLambda(lambda x: material_prompt.format_prompt(**x.get('materials'))),
            last=RunnableLambda(lambda x: self._generate_material(x)),
        )

        # 生成翻译的chain
        translation_chain = RunnableSequence(
            first=RunnableLambda(lambda x: _translation_prompt.format_prompt(**x)),
            last=RunnableLambda(lambda x: self._generate_translation(x)),
        )

        # 生成听力题目的 chain
        question_chain = RunnableSequence(
            first=RunnableLambda(lambda x: question_prompt.format_prompt(**x)),
            last=RunnableLambda(lambda x: self._generate_question(x)),
        )

        # 调用 chain 生成听力素材
        materials_res = material_chain.invoke({
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

        # 合并素材和参数，生成题目
        combined_args = self._combine_material_and_args(materials_res, args)

        parallel_chain = RunnableParallel(

            translation_chain=translation_chain,
            question_chain=question_chain,
        )
        res = parallel_chain.invoke(combined_args)
        print(res)
        question_result = res['question_chain']
        material_result = res['translation_chain']
        final_res = self.serialize_all(material_result=self.materials_obj['raw_content'],
                                       question_result=question_result, translation=material_result)

        # 打印生成的听力题目
        self._print(final_res)
        self.voice_material(final_res)
        return final_res
