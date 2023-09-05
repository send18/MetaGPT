#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:46
@Author  : alexanderwu
@File    : test_debug_error.py
"""
import pytest

from metagpt.actions.search_docs import SearchDocs
from metagpt.logs import logger

@pytest.mark.asyncio
async def test_search_docs_keyword():

    srch_doc = SearchDocs()

    msg = "上班时间"

    result = await srch_doc.run(question=msg, topk=3)

    logger.info(result)

@pytest.mark.asyncio
async def test_search_docs_natural_language():

    srch_doc = SearchDocs()

    msg = "我有一次9点40才到公司，是算迟到还是旷工？"

    result = await srch_doc.run(question=msg, topk=3)

    logger.info(result)