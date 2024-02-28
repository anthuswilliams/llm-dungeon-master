import agents.encounter_designer as ed
import agents.enemy as e
import agents.npc as npc

import json
from pydantic import BaseModel, Field
from typing import List, Type, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.agents import AgentFinish
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool, Tool

class StoryHook(BaseModel):
    description: str = Field("description of the story hook or encounter")
    encounter: ed.Encounter = Field("the encounter for the story hook")

class StoryFormatterArgs(BaseModel):
    hooks: List[StoryHook] = Field("the events the players will experience throughout the story")

class StoryFormatter(BaseTool):
    name = "StoryFormatter"
    description = "format a set of encounters"
    args_schema: Type[BaseModel] = StoryFormatterArgs

    def _run(
        self, hooks: List[StoryHook],
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        """Use the tool."""
        loggable = [s.model_dump() for s in hooks]
        return AgentFinish(return_values={"hooks": hooks}, log=json.dumps(loggable))
    
    async def _arun(
        self,
        hooks: List[str],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("does not support async")
    

system_prompt = """
You are a D&D dungeon master and a powerful storyteller. You are a student of Joseph Campbell and you know how to structure the beats of an adventure.

You will design a story involving 3 thematic story hooks. In keeping with Joseph Campbell's insights, the drama should increase as the story continues.
The setting and party for the adventure is: {input}

You have the following tools:
EncounterDesigner - use this to design encounters appropriate for the players' levels, desired difficulty. Use your generated story hook as the setting for this tool.
StoryFormatter - use this to structure the encounters in the desired output format

Output Format: return an array of the encounters in the adventure. Use `StoryFormatter` to structure them into the desired format.
{agent_scratchpad}
"""


def plan_story(input):
    tools = [
        ed.EncounterDesigner(),
        StoryFormatter()
    ]

    llm = ChatOpenAI(temperature=0.7)
    prompt = ChatPromptTemplate.from_template(template=system_prompt)
    agent = create_openai_tools_agent(llm, tools, prompt)

    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    # f u langchain I can return direct if I want to

    tools[-1].return_direct = True
    executor.invoke({"input": input})


if __name__ == "__main__":
    story = plan_story("setting: on a Spelljammer. party: level 1 barbarian, level 1 warlock")
    print(story["output"])