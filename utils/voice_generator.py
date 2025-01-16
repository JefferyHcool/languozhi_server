import os
import random
import uuid

import dashscope
from dashscope.audio.tts_v2 import *
from dotenv import load_dotenv

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


class VoiceGenerator:
    def __init__(self):
        load_dotenv()
        dashscope.api_key = os.getenv('DASH_SCOPE_API_KEY')
        self.model = "cosyvoice-v1"
        self.output_file = "combined_output.mp3"
        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.project_root = find_project_root(current_dir)
        self.voice_model = [
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
                "name": "longxiaobai",
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

    @property
    def voice_list(self) -> list:
        return self.voice_model

    def filter_by_gender(self, gender):
        """
        根据性别筛选出符合条件的对象，并随机返回一个。

        :param data: 包含字典的列表，每个字典包含 "name" 和 "gender" 键。
        :param gender: 需要筛选的性别（如 'm' 或 'f'）。
        :return: 随机筛选出的一个字典对象。
        """
        # 筛选出符合性别的对象
        filtered_data = [item for item in self.voice_model if item['gender'] == gender]

        # 如果没有符合条件的对象，返回 None
        if not filtered_data:
            return None

        # 随机选择一个对象
        return random.choice(filtered_data)
    def generate_voice(self, text: str,voice_model: str,file_name: str) -> str:
        """
        Generate voice from text.
        """
        callback = Callback()

        synthesizer = SpeechSynthesizer(model=self.model, voice=voice_model, speech_rate=1)
        audio = synthesizer.call(text)
        output_dir = os.path.join(self.project_root, 'file')
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'ab') as f:
            f.write(audio)
        return file_path

if __name__ == '__main__':
    generator = VoiceGenerator()
    generator.generate_voice('')