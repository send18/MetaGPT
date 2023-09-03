from __future__ import annotations

import importlib
import pathlib

import fire
import yaml
from loguru import logger
from pydantic import BaseModel

from metagpt.schema import Message


class AgentRoleConfig(BaseModel):
    name: str
    module: str = ""


class AgentStoreConfig(BaseModel):
    role: AgentRoleConfig


def load_role_cls(cls_name: str, module_name: str = ""):
    module_name = module_name or "metagpt.roles"
    module = importlib.import_module(module_name)
    return getattr(module, cls_name)


def load_default_role_cls(config_path: str = ".agent-store-config.yaml"):
    file_path = pathlib.Path(config_path)
    if not file_path.exists():
        raise FileNotFoundError(f"can not find the agent store role config file: {config_path}")
    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    logger.info(f"{config_path}: {data}")
    config = AgentStoreConfig(**data)
    return load_role_cls(config.role.name, config.role.module)


async def check_my_role(query: str = "what is metagpt?"):
    MyRoleCls = load_default_role_cls()
    my_role = MyRoleCls()
    my_role.recv(Message(content=query, cause_by="init"))
    tid = 0
    while 1:
        todo = await my_role.think()
        if not todo:
            break
        desc = todo.desc or str(todo)
        logger.info(f"The next todo: {desc}")
        resp = await my_role.act()
        if not resp.content:
            raise ValueError("Need act response")
        if not isinstance(resp.content, str):
            raise TypeError("The `resp.content` is not a string")
        logger.info(f"The {desc}: {resp.content}")
        tid += 1
    if not tid:
        raise ValueError("Need think result")


if __name__ == "__main__":
    fire.Fire(check_my_role)
