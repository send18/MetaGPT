import re
from typing import List

import requests
from pydantic import BaseModel

from metagpt.logs import logger
from metagpt.actions.action import Action

# URL = "http://192.168.50.134:8511/infer" # titan_gpu4
URL = "http://172.16.32.123:8511/infer" # ucloud-v100s-02

class Doc(BaseModel):
    item_id: str = ""
    text: str = ""
    score: float = 0.0

class DocResult(BaseModel):
    docs: List[Doc] = []

class SearchDocs(Action):
    def __init__(self, name="SearchDocs", context=None, llm=None):
        super().__init__(name, context, llm)        
    
    async def run(self, question, topk=5) -> List[DocResult]:

        logger.info(f"search for {question}")

        resp = requests.post(URL, json={"text": question, "topk": topk})

        assert resp.status_code == 200, f"Unexpected status code: {resp.status_code}"

        result = resp.json()

        result = DocResult(docs=[Doc(**item) for item in result["items"]])

        print(*result.docs, sep="\n")
        
        return result
