import os
from typing import Any, Coroutine

import aiofiles
from aiobotocore.session import get_session
from mdutils.mdutils import MdUtils
from zipstream import AioZipStream

from metagpt.actions import Action
from metagpt.actions.action_output import ActionOutput
from metagpt.actions.design_api import WriteDesign
from metagpt.actions.project_management import WriteTasks
from metagpt.actions.write_prd import WritePRD
from metagpt.config import CONFIG
from metagpt.roles import Architect, Engineer, ProductManager, ProjectManager, Role
from metagpt.schema import Message
from metagpt.software_company import SoftwareCompany as _SoftwareCompany


class RoleRun(Action):
    def __init__(self, role: Role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        action = role._actions[0]
        self.desc = f"{role.profile} {action.desc or str(action)}"


class PackProject(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.desc = "Pack the project with prd, design, code and more."

    async def run(self, key: str):
        url = await self.upload(key)
        mdfile = MdUtils(None)
        mdfile.new_paragraph(
            "We are thrilled to inform you that our project has been successfully packaged "
            "and is ready for download and use. You can download the packaged project through"
            f" the following link:\n[Project Download Link]({url})"
        )
        return ActionOutput(mdfile.get_md_text())

    async def upload(self, key: str):
        files = []
        workspace = CONFIG.workspace
        workspace = str(workspace)
        for r, _, fs in os.walk(workspace):
            _r = r[len(workspace) :].lstrip("/")
            for f in fs:
                files.append({"file": os.path.join(r, f), "name": os.path.join(_r, f)})
        # aiozipstream
        chunks = []
        async for chunk in AioZipStream(files, chunksize=32768).stream():
            chunks.append(chunk)
        return await upload_to_s3(b"".join(chunks), key)


class SoftwareCompany(Role):
    """封装软件公司成角色，以快速接入agent store。"""

    def __init__(self, name="", profile="", goal="", constraints="", desc="", *args, **kwargs):
        super().__init__(name, profile, goal, constraints, desc, *args, **kwargs)
        company = _SoftwareCompany()
        company.hire([ProductManager(), Architect(), ProjectManager(), Engineer(n_borg=5)])
        self.company = company
        self.uid = CONFIG.workspace.name
        self.engineer: Engineer = None
        self.finish = False
        self._init_actions([PackProject])

    def recv(self, message: Message) -> None:
        self.company.start_project(message.content)

    async def _think(self) -> Coroutine[Any, Any, bool]:
        """软件公司运行需要4轮

        BOSS            -> ProductManager -> Architect   -> ProjectManager -> Engineer
        BossRequirement -> WritePRD       -> WriteDesign -> WriteTasks     -> WriteCode
        """
        if self.finish:
            self._rc.todo = None
            return False

        if self.engineer:
            if self.engineer.todos:
                todo = self.engineer.todos[0]
                self._rc.todo.desc = f"Engineer Write Code: {todo}."
                return True
            else:
                self._set_state(0)
                return True

        environment = self.company.environment
        for role in environment.roles.values():
            observed = environment.memory.get_by_actions(role._rc.watch)
            memory = role._rc.memory.get()
            for i in observed:
                if i not in memory:
                    self._rc.todo = RoleRun(role)
                    if isinstance(role, Engineer):
                        self.engineer = role
                        await self.engineer._observe()
                        return await self._think()
                    return True

        self._rc.todo = None
        return False

    async def _act(self) -> Message:
        if isinstance(self._rc.todo, PackProject):
            name = self.engineer.get_workspace().name
            key = f"{self.uid}/metagpt-{name}.zip"
            output = await self._rc.todo.run(key)
            self.finish = True
            return Message(output.content, role=self.profile, cause_by=type(self._rc.todo))

        if self.engineer:
            if self.engineer.todos:
                code = await self.engineer.write_code()
                output = await self.format_code(code)
            else:
                raise RuntimeError("Nothing to do")
        else:
            await self.company.run(1)
            output = self.company.environment.memory.get(1)[0]
            cause_by = output.cause_by

            if cause_by is WritePRD:
                output = await self.format_prd(output)
            elif cause_by is WriteDesign:
                output = await self.format_system_design(output)
            elif cause_by is WriteTasks:
                output = await self.format_task(output)
        return output

    async def format_prd(self, prd: Message):
        workspace = CONFIG.workspace
        data = prd.instruct_content.dict()
        mdfile = MdUtils(None)
        title = "Original Requirements"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_paragraph(data[title])

        title = "Product Goals"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_list(data[title], marked_with="1")

        title = "User Stories"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_list(data[title], marked_with="1")

        title = "Competitive Analysis"
        mdfile.new_header(2, title, add_table_of_contents=False)
        if all(i.count(":") == 1 for i in data[title]):
            mdfile.new_table(
                2, len(data[title]) + 1, ["Competitor", "Description", *(i for j in data[title] for i in j.split(":"))]
            )
        else:
            mdfile.new_list(data[title], marked_with="1")

        title = "Competitive Quadrant Chart"
        mdfile.new_header(2, title, add_table_of_contents=False)
        competitive_analysis_path = workspace / "resources" / "competitive_analysis.png"
        if competitive_analysis_path.exists():
            key = f"{self.uid}/resources/competitive_analysis.png"
            url = await upload_file_to_s3(competitive_analysis_path, key)
            mdfile.new_line(mdfile.new_inline_image(title, url))
        else:
            mdfile.insert_code(data[title], "mermaid")

        title = "Requirement Analysis"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_paragraph(data[title])

        title = "Requirement Pool"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_table(
            2, len(data[title]) + 1, ["Task Description", "Priority", *(i for j in data[title] for i in j)]
        )

        title = "UI Design draft"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_paragraph(data[title])

        title = "Anything UNCLEAR"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_paragraph(data[title])
        return Message(mdfile.get_md_text(), cause_by=prd.cause_by, role=prd.role)

    async def format_system_design(self, design: Message):
        workspace = CONFIG.workspace
        data = design.instruct_content.dict()
        mdfile = MdUtils(None)

        title = "Implementation approach"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_paragraph(data[title])

        title = "Python package name"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.insert_code(data[title], "python")

        title = "File list"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_list(data[title], marked_with="1")

        title = "Data structures and interface definitions"
        mdfile.new_header(2, title, add_table_of_contents=False)
        data_api_design_path = workspace / "resources" / "data_api_design.png"
        if data_api_design_path.exists():
            key = f"{self.uid}/resources/data_api_design.png"
            url = await upload_file_to_s3(data_api_design_path, key)
            mdfile.new_line(mdfile.new_inline_image(title, url))
        else:
            mdfile.insert_code(data[title], "mermaid")

        title = "Program call flow"
        mdfile.new_header(2, title, add_table_of_contents=False)
        seq_flow_path = workspace / "resources" / "seq_flow.png"
        if seq_flow_path.exists():
            key = f"{self.uid}/resources/seq_flow.png"
            url = await upload_file_to_s3(seq_flow_path, key)
            mdfile.new_line(mdfile.new_inline_image(title, url))
        else:
            mdfile.insert_code(data[title], "mermaid")

        title = "Anything UNCLEAR"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_paragraph(data[title])
        return Message(mdfile.get_md_text(), cause_by=design.cause_by, role=design.role)

    async def format_task(self, task: Message):
        data = task.instruct_content.dict()
        mdfile = MdUtils(None)
        title = "Required Python third-party packages"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.insert_code(data[title], "python")

        title = "Required Other language third-party packages"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.insert_code(data[title], "python")

        title = "Full API spec"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.insert_code(data[title], "python")

        title = "Logic Analysis"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_table(
            2, len(data[title]) + 1, ["Filename", "Class/Function Name", *(i for j in data[title] for i in j)]
        )

        title = "Task list"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.new_list(data[title])

        title = "Shared Knowledge"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.insert_code(data[title], "python")

        title = "Anything UNCLEAR"
        mdfile.new_header(2, title, add_table_of_contents=False)
        mdfile.insert_code(data[title], "python")
        return Message(mdfile.get_md_text(), cause_by=task.cause_by, role=task.role)

    async def format_code(self, code: Message):
        data = code.instruct_content.dict()

        mdfile = MdUtils(None)
        filename = data["filename"]
        content = data["content"]
        suffix = filename.rsplit(".", maxsplit=1)[-1]
        mdfile.insert_code(content, "python" if suffix == "py" else suffix)
        return Message(mdfile.get_md_text(), cause_by=code.cause_by, role=code.role)


async def upload_file_to_s3(filepath: str, key: str):
    async with aiofiles.open(filepath, "rb") as f:
        content = await f.read()
        return await upload_to_s3(content, key)


async def upload_to_s3(content: bytes, key: str):
    session = get_session()
    async with session.create_client(
        "s3",
        aws_secret_access_key=CONFIG.get("S3_SECRET_KEY"),
        aws_access_key_id=CONFIG.get("S3_ACCESS_KEY"),
        endpoint_url=CONFIG.get("S3_ENDPOINT_URL"),
        use_ssl=CONFIG.get("S3_SECURE"),
    ) as client:
        # upload object to amazon s3
        bucket = CONFIG.get("S3_BUCKET")
        await client.put_object(Bucket=bucket, Key=key, Body=content)
        return f"{CONFIG.get('S3_ENDPOINT_URL')}/{bucket}/{key}"
