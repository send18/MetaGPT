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

PROMPT_TEMPLATE_EN = """
You are an internal consultant in the company responsible for answering employee's questions about company policies,
you should answer questions based on company documents, you will be able to search a document text collections for the relevant documents.
##
You have a context below:
{context}
##
Now you should decide if the question is about company policies:
1. if it is and you need to search the document text collections, issue an instruction SEARCH + the query phrase, where the query phrase is rewritten from the original question for better text retrieval performance;
2. if it is but you can directly answer the question based on the context, issue an instruction ANSWER_DIRECTLY;
3. if it isn't, that is, the question is not relevant to company policies, issue an instruction REJECT_ANSWER;
##
The question is:
{question}
##
Your instruction:
"""


PROMPT_TEMPLATE = """
你是公司的内部顾问，负责回答员工关于公司政策的问题，你应根据公司文档来回答问题，你可以在文档文本集合中搜索相关文档。
##
以下是上下文:
{context}
##
现在你应该判定这个问题是否与公司政策有关：
如果是，并且你需要搜索文档文本的集合，发出指令 SEARCH+查询短语，其中查询短语可通过改写原始问题得到，目的是更好地进行文档文本的检索；
如果是，但你可以根据上下文直接回答这个问题，发出指令 ANSWER_DIRECTLY；
如果不是，也就是说，这个问题与公司政策无关，发出指令 REJECT_ANSWER。
##
问题:
{question}
##
你输出的指令:
"""

class QueryUnderstand(Action):
    def __init__(self, name="QueryUnderstand", context=None, llm=None):
        super().__init__(name, context, llm)
    
    async def run(self, question, context=""):

        logger.info(f"QU for {question}")

        prompt = PROMPT_TEMPLATE.format(question=question, context=context)
        
        rsp = await self._aask(prompt)

        return rsp
