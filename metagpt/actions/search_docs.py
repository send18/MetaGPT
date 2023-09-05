import aiohttp
from pydantic import BaseModel

from metagpt.actions.action import Action
from metagpt.logs import logger

URL = "http://192.168.50.134:8511/infer"  # titan_gpu4
# URL = "http://172.16.32.123:8511/infer"  # ucloud-v100s-02


class Doc(BaseModel):
    item_id: str = ""
    text: str = ""
    score: float = 0.0


class DocResult(BaseModel):
    docs: list[Doc] = []


class SearchDocs(Action):
    def __init__(self, name="SearchDocs", context=None, llm=None):
        super().__init__(name, context, llm)

    async def run(self, question, topk=5) -> list[DocResult]:
        logger.info(f"search for {question}")

        async with aiohttp.ClientSession() as client:
            async with client.post(URL, json={"text": question, "topk": topk}) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Unexpected status code: {resp.status_code}")

        result = await resp.json()
        result = DocResult(docs=[Doc(**item) for item in result["items"]])
        return result
