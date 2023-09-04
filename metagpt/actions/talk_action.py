#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/28
@Author  : mashenquan
@File    : talk_action.py
@Desc    : Act as it’s a talk
"""

from metagpt.actions import Action, ActionOutput
from metagpt.config import CONFIG
from metagpt.const import DEFAULT_LANGUAGE
from metagpt.logs import logger


class TalkAction(Action):
    def __init__(self, name: str = "", talk="", history_summary="", knowledge="", context=None, llm=None, **kwargs):
        context = context or {}
        context["talk"] = talk
        context["history_summery"] = history_summary
        context["knowledge"] = knowledge
        super(TalkAction, self).__init__(name=name, context=context, llm=llm)
        self._talk = talk
        self._history_summary = history_summary
        self._knowledge = knowledge
        self._rsp = None

    @property
    def prompt(self):
        prompt = ""
        if CONFIG.agent_description:
            prompt = (
                f"You are {CONFIG.agent_description}. Your responses should align with the role-play agreement, "
                f"maintaining the character's persona and habits. When faced with unrelated questions, playfully "
                f"decline to answer without revealing your AI nature to preserve the character's image.\n\n"
            )
        prompt += f"Background knowledge:\n{self._knowledge}\n\n" if self._knowledge else ""
        prompt += f"{self._history_summary}\n\n"
        if self._history_summary != "":
            prompt += "According to the historical conversation above, "
        language = CONFIG.language or DEFAULT_LANGUAGE
        prompt += (
            f"Answer the following questions in {language}, and the answers must follow the Markdown format.\n "
            f"{self._talk}"
        )
        return prompt

    async def run(self, *args, **kwargs) -> ActionOutput:
        prompt = self.prompt
        logger.info(prompt)
        rsp = await self.llm.aask(msg=prompt, system_msgs=[])
        logger.info(rsp)
        self._rsp = ActionOutput(content=rsp)
        return self._rsp
