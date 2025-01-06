import os
from typing import AnyStr

from captcha.image import ImageCaptcha
from PIL import Image, ImageDraw, ImageFont
import random


class CaptchaService():
    def __init__(self):

        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.dirname(current_dir)

        self.captcha = ImageCaptcha()

    def generate_captcha(self, code: AnyStr):

        code = self.captcha.generate(code)
        return code


