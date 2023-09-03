import random

from loguru import logger

from metagpt.actions.my_action import MyAction1, MyAction2, MyAction3
from metagpt.roles import Role
from metagpt.schema import Message


class MyRole(Role):
    def __init__(
        self,
        name="My Name",
        profile="My Profile",
        goal="The example goal",
        constraints="The example constraints",
        desc="The example role",
        *args,
        **kwargs,
    ):
        super().__init__(name, profile, goal, constraints, desc, *args, **kwargs)
        self._init_actions([MyAction1, MyAction2, MyAction3])

    async def _think(self) -> bool:
        # My think
        if self._rc.todo is None:
            self._set_state(random.choice([i for i in range(len(self._actions))]))
        else:
            self._rc.todo = None

    async def _act(self) -> Message:
        # My act
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        requirement = self._rc.memory.get(1)[0]
        response = await self._rc.todo.run(requirement.content)
        msg = Message(content=response.content, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)

        return msg
