import logging
import os
import random
import uuid
from typing import List, Dict, Any, Optional

import dashscope
import dotenv
from dashscope.audio.tts_v2 import *
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def find_project_root(current_dir):
    """
    递归向上查找工程根目录。
    默认以包含 .git 文件夹的目录为工程根目录。
    """
    # 检查当前目录是否包含 .git 文件夹
    if os.path.isdir(os.path.join(current_dir, '.git')):
        return current_dir
    # 获取上一级目录
    parent_dir = os.path.dirname(current_dir)
    # 如果已经到达文件系统根目录，停止递归
    if parent_dir == current_dir:
        raise FileNotFoundError("无法找到工程根目录（未找到 .git 文件夹）。")
    # 递归查找
    return find_project_root(parent_dir)
class Callback(ResultCallback):
    _player = None
    _stream = None

    def on_open(self):
        self.file = open("output.mp3", "wb")
        print("websocket is open.")

    def on_complete(self):
        with open("output.mp3", "wb") as f:
            data=self.file.read()
            f.write(data)
        print("speech synthesis task complete successfully.")

    def on_error(self, message: str):
        print(f"speech synthesis task failed, {message}")

    def on_close(self):
        print("websocket is closed.")
        self.file.close()

    def on_event(self, message):
        print(f"recv speech synthsis message {message}")

    def on_data(self, data: bytes) -> None:
        print("audio result length:", len(data))
        self.file.write(data)

ALI_MODEL=[
            {
                "name": "longwan",
                'gender': 'f'
            },
            {
                "name": "longcheng",
                'gender': 'm'
            },
            {
                "name": "longhua",
                'gender': 'f'
            },
            {
                "name": "longxiaochun",
                'gender': 'f'
            },
            {
                "name": "longshu",
                'gender': 'm'
            },
            {
                "name": "longshuo",
                'gender': 'm'
            },
            {
                "name": "longjing",
                'gender': 'f'
            },
            {
                "name": "longmiao",
                'gender': 'f'
            },
            {
                "name": "longyue",
                'gender': 'f'
            },
            {
                "name": "longyuan",
                'gender': 'f'
            },
            {
                "name": "loongstella",
                'gender': 'f'
            },
            {
                "name": "Bella",
                'gender': 'f'
            },
        ]

AZURE_MODEL=[
    {
        "name": "en-US-AvaMultilingualNeural",
        'gender': 'f'
    },
    {
        "name": "en-US-AndrewMultilingualNeural",
        'gender': 'm'
    },
    {
        "name": "en-US-EmmaMultilingualNeural",
        'gender': 'f'
    },
    {
        "name": "en-US-BrianMultilingualNeural",
        'gender': 'm'
    },
    {
        "name": "en-US-AvaNeural",
        'gender': 'f'
    }

]
class VoiceGenerator:
    def __init__(self):
        dotenv.load_dotenv()
        dashscope.api_key = os.getenv('DASH_SCOPE_API_KEY')
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get('SPEECH_KEY'),
            region=os.environ.get('SPEECH_REGION')
        )
        self.model = "cosyvoice-v1"
        self.output_file = "combined_output.wav"  # 默认输出文件名
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = find_project_root(current_dir)
        self.voice_model = AZURE_MODEL  # 假设 AZURE_MODEL 是一个预定义的语音模型列表
        self.stream = None

    @property
    def voice_list(self) -> List[Dict[str, Any]]:
        return self.voice_model

    def filter_by_gender(self, gender: str) -> Dict[str, Any]:
        """
        根据性别筛选出符合条件的对象，并随机返回一个。

        :param gender: 需要筛选的性别（如 'm' 或 'f'）。
        :return: 随机筛选出的一个字典对象。
        """
        filtered_data = [item for item in self.voice_model if item['gender'] == gender]
        if not filtered_data:
            logger.warning(f"No voice model found for gender: {gender}")
            return None
        return random.choice(filtered_data)

    def generate_ssml(self, speaker_model: str, content:str) -> str:
        """
        生成包含多轮对话的SSML字符串。

        参数:
        - speaker_model: 一个字典，包含说话人和对应的语音模型
        - material: 包含对话内容的列表

        返回:
        - 生成的SSML字符串
        """
        ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">'

        return  f'<voice name="{speaker_model}">{content}</voice>'

        # ssml += '</speak>'
        # return ssml
    def generate_voice(self, text: str, voice_model: str, file_name: str,ssml:Optional[bool]=False) -> str:
        """
        使用 Azure 语音合成服务生成语音文件，并保存为 .wav 文件。

        :param text: 要合成的文本。
        :param voice_model: 语音模型名称。
        :param file_name: 输出文件名。
        :return: 生成的语音文件路径。
        """
        output_dir = os.path.join(self.project_root, 'file')  # 输出目录
        os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
        file_path = os.path.join(output_dir, file_name)

        if ssml:
            print(f"Generating voice for text: {text}")
            speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)

            speech_synthesis_result = speech_synthesizer.speak_ssml_async(text).get()
            print(speech_synthesis_result)
            stream = speechsdk.AudioDataStream(speech_synthesis_result)
            stream.save_to_wav_file(file_path)
            return file_path

        self.speech_config.speech_synthesis_language = "en-US"
        self.speech_config.speech_synthesis_voice_name = voice_model

        # 配置音频输出为文件
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_path)

        # 创建语音合成器
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=None  # 不使用默认音频输出
        )

        try:
            # 合成语音
            result = speech_synthesizer.speak_text_async(text).get()
            # stream = speechsdk.AudioDataStream(speech_synthesis_result)
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                stream = speechsdk.AudioDataStream()
                stream.write(result.audio_data)
                logger.info(f"Appended voice for text: {text}")

            # 检查合成结果

        except Exception as e:
            logger.error(f"An error occurred during speech synthesis: {e}")
            raise

        return file_path



if __name__ == '__main__':
    generator = VoiceGenerator()
    ssml='''
    <speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-AndrewMultilingualNeural">Hey, have you seen the new Marvel movie?</voice>
        <voice name="en-US-EmmaMultilingualNeural">Yes, I watched it last weekend. It was amazing!</voice>
    </speak>

    '''
    generator.generate_voice(text=ssml, voice_model="en-US-AvaMultilingualNeural"
                             ,file_name="1.wav" ,ssml=True)