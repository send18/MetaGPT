#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:46
@Author  : alexanderwu
@File    : test_debug_error.py
"""
import pytest

from metagpt.actions.summarize_docs import SummarizeDocs, DocResult, Doc
from metagpt.logs import logger

@pytest.mark.asyncio
async def test_summarize_docs_answer():

    smr_doc = SummarizeDocs()

    msg = "我有一次9点40才到公司，是算迟到还是旷工？"

    texts = [
        """二、作息时间：每周工作六天,加班可于事后调休(协商处理）。
        上午：9：30 ～ 12：00
        下午:13：30 ~ 18:00
        如有调整，以新公布的工作时间为准.""",

        """五、活动安排：每个部门在每周三晚组织团队活动，可聚餐、桌游、开展体育活动等""",

        """三、考勤(请假不超过两天的需提前一天提出请假申请，超过两天的需提前三天提出请假申请)
        1、公司员工上、下班（30分钟以内为迟到或早退、30分钟以上则视为旷工）迟到、早退一次， 迟到或早退四次以上无全勤奖（含四次),请假1天不扣全勤奖，请假2天视情况定，超过2天以上的扣全勤奖另扣超过2天以上部分天数（基本工资÷30×请假天数×3）计算。超过六天视为严重违纪（按新员工入职标准执行重新入职）。
        2、无故不办理请假手续,而擅自不上班，按旷工处理。""",
    ]
    doc_result = DocResult(docs=[Doc(text=text) for text in texts])

    rsp = await smr_doc.run(question=msg, doc_result=doc_result)
    
    assert "#[0]#" in rsp
    assert "#[2]#" in rsp

@pytest.mark.asyncio
async def test_summarize_docs_cant_answer():

    smr_doc = SummarizeDocs()

    msg = "我有一次9点40才到公司，是算迟到还是旷工？"

    texts = [
        """三、考勤(请假不超过两天的需提前一天提出请假申请，超过两天的需提前三天提出请假申请)
        1、公司员工上、下班（30分钟以内为迟到或早退、30分钟以上则视为旷工）迟到、早退一次， 迟到或早退四次以上无全勤奖（含四次),请假1天不扣全勤奖，请假2天视情况定，超过2天以上的扣全勤奖另扣超过2天以上部分天数（基本工资÷30×请假天数×3）计算。超过六天视为严重违纪（按新员工入职标准执行重新入职）。
        2、无故不办理请假手续,而擅自不上班，按旷工处理。""",
    ]
    doc_result = DocResult(docs=[Doc(text=text) for text in texts])

    rsp = await smr_doc.run(question=msg, doc_result=doc_result)

    assert "#[" not in rsp

@pytest.mark.asyncio
async def test_summarize_docs_cant_answer_wo_context():

    smr_doc = SummarizeDocs()

    msg = "我有一次9点40才到公司，是算迟到还是旷工？"

    rsp = await smr_doc.run(question=msg, doc_result=None)

@pytest.mark.asyncio
async def test_summarize_docs_reject_answer():

    smr_doc = SummarizeDocs()

    msg = "今天的天气如何"

    rsp = await smr_doc.run(question=msg, doc_result=None)
