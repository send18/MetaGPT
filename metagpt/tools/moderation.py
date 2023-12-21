# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/26 14:27
@Author  : zhanglei
@File    : moderation.py
"""
from typing import Union

from metagpt.llm import LLMFactory


class Moderation:
    def __init__(self):
        self.llm = LLMFactory.new_llm()

    def handle_moderation_results(self, results):
        resp = []
        for item in results:
            categories = item.categories
            true_categories = [category for category, item_flagged in categories.items() if item_flagged]
            resp.append({"flagged": item.flagged, "true_categories": true_categories})
        return resp

    def moderation(self, content: Union[str, list[str]]):
        resp = []
        if content:
            moderation_results = self.llm.moderation(content=content)
            resp = self.handle_moderation_results(moderation_results.results)
        return resp

    async def amoderation(self, content: Union[str, list[str]]):
        resp = []
        if content:
            moderation_results = await self.llm.amoderation(content=content)
            resp = self.handle_moderation_results(moderation_results.results)
        return resp


if __name__ == "__main__":
    moderation = Moderation()
    print(moderation.moderation(content=["I will kill you", "The weather is really nice today", "I want to hit you"]))