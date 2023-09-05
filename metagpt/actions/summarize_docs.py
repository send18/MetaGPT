#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/4 17:46
@Author  : garylin2099
@File    : query_understand.py
"""
import re

from metagpt.logs import logger
from metagpt.actions.action import Action
from metagpt.actions.search_docs import Doc, DocResult

PROMPT_TEMPLATE_EN = """
You are an internal consultant in the company responsible for answering employee's questions about company policies.
Based on company documents retrieved, answer the question as much as you can, cite relevant sources of information that support your answer.
ATTENTION: DO NOT make up an answer, if there is not enough information to answer the question or if the question is not relevant to company policies, say you do not know.
## Example
Question: this is my second year in the company, how much paid time off do I have?
Company Docs:
#*[1]*# First-year employees have 10 days off
#*[2]*# Employees who have been in the company for 1 to 3 years have 15 days off
#*[3]*# Employees who have been in the company for 3 years and more have 20 days off
#*[4]*# Each department is responsible for organizing departmental events montly.
Answer:
Since you have worked for 2 years in the company, based on "Employees who have been in the company for 1 to 3 years have 15 days off" #*[2]*#,
you have 15 days off.
##
The question is:
{question}
##
You found company docs below, each doc is split by #*[index]*#:
{context}
##
Your answer:
"""

PROMPT_TEMPLATE = """
你在公司中担任内部顾问，负责回答员工关于公司政策的问题。
根据检索到的公司文档，尽可能地回答问题，并引用支持你答案的相关信息来源，以#[数字]#表示。
注意：如果没有足够的信息来回答问题，或者问题与公司政策无关，请不要编造答案，直接说你不知道。
----
Example
问题：我在公司工作了两年，我有多少带薪休假时间？
公司文件：
#[1]#
考勤：员工应于早上10:00前打卡上班
#[2]#
三、休假制度
1. 第一年的员工有10天休假。
2. 在公司工作1到3年的员工有15天休假。
3. 在公司工作3年及以上的员工有20天休假。
#[2]#
五、公司团建：每个部门负责每月组织部门活动。
回答：
由于您在公司工作了2年，根据#[2]#中的“在公司工作1到3年的员工有15天休假”，您有15天休假。
---
##
问题:
{question}
##
公司文档（每份文档由#[数字]#标识）:
{context}
##
你的回答:
"""

class SummarizeDocs(Action):
    def __init__(self, name="SummarizeDocs", context=None, llm=None):
        super().__init__(name, context, llm)
    
    async def run(self, question: str, doc_result: DocResult = None):
        context = []
        idx2docid = {}
        if doc_result:
            for idx, doc in enumerate(doc_result.docs):
                context.append(f"#[{idx}]#\n{doc.text}")
                idx2docid[f"#[{idx}]#"] = doc.item_id
        context = "\n".join(context)

        prompt = PROMPT_TEMPLATE.format(question=question, context=context)
        # logger.info(prompt)

        rsp = await self._aask(prompt)

        return rsp
