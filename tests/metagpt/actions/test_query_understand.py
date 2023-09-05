#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:46
@Author  : alexanderwu
@File    : test_debug_error.py
"""
import pytest

from metagpt.actions.query_understand import QueryUnderstand
from metagpt.logs import logger

@pytest.mark.asyncio
async def test_qu_need_search():

    qu = QueryUnderstand()

    msg = "我有一次9点40才到公司，是算迟到还是旷工？"

    context = """
    """

    instruction = await qu.run(question=msg, context=context)

    logger.info(instruction)
    assert "SEARCH" in instruction

@pytest.mark.asyncio
async def test_qu_answer_directly():

    qu = QueryUnderstand()

    msg = "我有一次9点40才到公司，是算迟到还是旷工？"

    context = """
    二、作息时间：每周工作六天,加班可于事后调休(协商处理）。
        上午：9：30 ～ 12：00
        下午:13：30 ~ 18:00
        如有调整，以新公布的工作时间为准.
    三、考勤(请假不超过两天的需提前一天提出请假申请，超过两天的需提前三天提出请假申请)
    1、公司员工上、下班（30分钟以内为迟到或早退、30分钟以上则视为旷工）迟到、早退一次， 迟到或早退四次以上无全勤奖（含四次),请假1天不扣全勤奖，请假2天视情况定，超过2天以上的扣全勤奖另扣超过2天以上部分天数（基本工资÷30×请假天数×3）计算。超过六天视为严重违纪（按新员工入职标准执行重新入职）。
    2、无故不办理请假手续,而擅自不上班，按旷工处理。
    """

    instruction = await qu.run(question=msg, context=context)
    
    assert instruction == "ANSWER_DIRECTLY"

@pytest.mark.asyncio
async def test_qu_reject_answer():

    qu = QueryUnderstand()

    msg = "今天的天气如何"

    context = """
    """

    instruction = await qu.run(question=msg, context=context)
    
    assert instruction == "REJECT_ANSWER"
