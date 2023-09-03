from metagpt.actions import Action
from metagpt.actions.action_output import ActionOutput


class MyAction1(Action):
    def __init__(self, name: str = "MyAction1", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.desc = "Action 1"

    async def run(self, prompt) -> ActionOutput:
        content = await self.llm.aask(prompt)
        # process the content

        # Create an instruct_content if available
        instruct_content = None

        return ActionOutput(content=content, instruct_content=instruct_content)


class MyAction2(Action):
    def __init__(self, name: str = "MyAction2", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.desc = "Action 2"

    async def run(self, prompt) -> ActionOutput:
        content = await self.llm.aask(prompt)
        # process the content

        # Create an instruct_content if available
        instruct_content = None

        return ActionOutput(content=content, instruct_content=instruct_content)


class MyAction3(Action):
    def __init__(self, name: str = "MyAction3", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.desc = "Action 3"

    async def run(self, prompt) -> ActionOutput:
        content = await self.llm.aask(prompt)
        # process the content

        # Create an instruct_content if available
        instruct_content = None

        return ActionOutput(content=content, instruct_content=instruct_content)
