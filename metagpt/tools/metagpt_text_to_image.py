#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18
@Author  : mashenquan
@File    : metagpt_text_to_image.py
@Desc    : MetaGPT Text-to-Image OAS3 api, which provides text-to-image functionality.
"""
import asyncio
import base64
import os
import sys
from pathlib import Path
from typing import List, Dict

import aiohttp
import requests
from pydantic import BaseModel

from metagpt.config import CONFIG, Config

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))  # fix-bug: No module named 'metagpt'
from metagpt.logs import logger


class MetaGPTText2Image:
    def __init__(self, model_url):
        """
        :param model_url: Model reset api url
        """
        self.model_url = model_url if model_url else CONFIG.METAGPT_TEXT_TO_IMAGE_MODEL

    async def text_2_image(self, text, size_type="512x512"):
        """Text to image

        :param text: The text used for image conversion.
        :param size_type: One of ['512x512', '512x768']
        :return: The image data is returned in Base64 encoding.
        """

        headers = {
            "Content-Type": "application/json"
        }
        dims = size_type.split("x")
        data = {
            "prompt": text,
            "negative_prompt": "(easynegative:0.8),black, dark,Low resolution",
            "override_settings": {"sd_model_checkpoint": "galaxytimemachinesGTM_photoV20"},
            "seed": -1,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 20,
            "cfg_scale": 11,
            "width": int(dims[0]),
            "height": int(dims[1]),  # 768,
            "restore_faces": False,
            "tiling": False,
            "do_not_save_samples": False,
            "do_not_save_grid": False,
            "enable_hr": False,
            "hr_scale": 2,
            "hr_upscaler": "Latent",
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "hr_upscale_to_x": 0,
            "hr_upscale_to_y": 0,
            "truncate_x": 0,
            "truncate_y": 0,
            "applied_old_hires_behavior_to": None,
            "eta": None,
            "sampler_index": "DPM++ SDE Karras",
            "alwayson_scripts": {},
        }

        class ImageResult(BaseModel):
            images: List
            parameters: Dict

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.model_url, headers=headers, json=data) as response:
                    result = ImageResult(**await response.json())
            if len(result.images) == 0:
                return ""
            return result.images[0]
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred:{e}")
        return ""


# Export
async def oas3_metagpt_text_to_image(text, size_type: str = "512x512", model_url=""):
    """Text to image

    :param text: The text used for image conversion.
    :param model_url: Model reset api
    :param size_type: One of ['512x512', '512x768']
    :return: The image data is returned in Base64 encoding.
    """
    if not text:
        return ""
    if not model_url:
        model_url = CONFIG.METAGPT_TEXT_TO_IMAGE_MODEL_URL
    return await MetaGPTText2Image(model_url).text_2_image(text, size_type=size_type)


if __name__ == "__main__":
    Config()
    loop = asyncio.new_event_loop()
    task = loop.create_task(oas3_metagpt_text_to_image("Panda emoji"))
    v = loop.run_until_complete(task)
    print(v)
    data = base64.b64decode(v)
    with open("tmp.png", mode="wb") as writer:
        writer.write(data)
    print(v)
