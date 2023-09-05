from metagpt.actions.query_understand import QueryUnderstand
from metagpt.actions.search_docs import SearchDocs
from metagpt.actions.summarize_docs import SummarizeDocs
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message


class CompanyConsultant(Role):
    def __init__(
        self,
        name: str = "Chloe",
        profile: str = "CompanyConsultant",
        goal: str = "Answer employee's questionsb about company policies based on company documents",
        constraints: str = "Ensure accuracy and relevance of information",
        **kwargs,
    ):
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions([QueryUnderstand, SearchDocs, SummarizeDocs])
        self.original_question = None
        self.rewritten_query = None

    async def _think(self) -> None:
        if self._rc.todo is None:
            # set state to initial before starting or after one cycle
            self._set_state(0)
            return

        previous_state = self._rc.state
        if previous_state == 0:
            # previous state is QU, decide next action based on QU result
            qu_result = self._rc.memory.get(k=1)[0]
            current_state = self._parse_qu_result(qu_result)  # can be 1 or 2
            self._set_state(current_state)
        elif previous_state == 1:
            # search done, summarize
            self._set_state(2)
        elif previous_state == 2:
            # summarize done, a cycle completed, set state back to intital
            self._set_state(0)
            self._rc.todo = None

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        todo = self._rc.todo
        msg = self._rc.memory.get()[-1]

        if isinstance(todo, QueryUnderstand):
            self.original_question = msg.content
            rsp = await QueryUnderstand().run(question=self.original_question)
            msg = Message(content=rsp, role=self.profile, cause_by=todo)

        elif isinstance(todo, SearchDocs):
            question = self.original_question  # NOTE: or use self.rewritten_query
            rsp = await SearchDocs().run(question=question, topk=3)
            msg = Message(content="", instruct_content=rsp, role=self.profile, cause_by=todo)

        elif isinstance(todo, SummarizeDocs):
            doc_result = (
                msg.instruct_content
            )  # might be None (from QueryUnderstand) or a DocResult object (from SearchDocs)
            rsp = await SummarizeDocs().run(question=self.original_question, doc_result=doc_result)
            msg = Message(content=rsp, role=self.profile, cause_by=todo)

        self._rc.memory.add(msg)
        return msg

    async def _react(self) -> Message:
        while True:
            await self._think()
            if self._rc.todo is None:
                break
            await self._act()
        return Message(content="One conversation done", role=self.profile)  # FIXME

    def _parse_qu_result(self, qu_rsp):
        content = qu_rsp.content
        if "SEARCH" in content:
            self.rewritten_query = content.split("+")[-1]  # hard code splitter for now
            return 1
        else:
            return 2


if __name__ == "__main__":
    import fire

    async def main(question: str):
        role = CompanyConsultant()
        logger.info(question)
        await role.run(question)

    fire.Fire(main)
