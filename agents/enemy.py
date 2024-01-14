from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain import hub
from langchain.pydantic_v1 import BaseModel, Field

import random
from typing import List
import re

prompt_template = """
You are a {name} in a game of Dungeons & Dragons 5th edition.  You will be identified by the name {identifier}.
Here is your character sheet: {stats}
Actions: {actions}
Other Info: {other_info}

When you are asked to make a roll, you (a) roll the dice using the RollDice() function,
and then (b) apply any modifiers as indicated by your character sheet.
IMPORTANT!!! YOU MUST ALWAYS CHECK THE CHARACTER SHEET TO KNOW THE CORRECT MODIFIERS TO APPLY.

Example:
I rolled a 4. I have [[initiative modifier]] on initiative, so my initiative is [[4 + initiative_modifier]]
"""


def create_enemy_prompt(name, stat_block, identifier):
    # some sort of weird behavior in lang-chain causes the json-encoded stat block to be sought as
    #  fields on some intermediate class; converting to a simple text format avoids this problem. In theory, anyway.
    text_stats = "\n".join([f"{k}: {v}" for k, v in stat_block["stats"].items()])
    text_actions = "\n".join(
        [f'{a["name"]} - {a["description"]}' for a in stat_block["actions"]]
    )
    prompt = prompt_template.format(
        name=name,
        identifier=identifier,
        stats=text_stats,
        actions=text_actions,
        other_info=stat_block["other_info"],
    )
    return prompt


def dice_roll(query: str) -> List[int]:
    results = re.search(r"^(\d+)d(\d+)$", query)
    if not results:
        raise ValueError(f"query {query} is uninterpretable")

    num = results.group(1)
    val = results.group(2)

    return [random.randint(1, int(val)) for i in range(int(num))]


tools = [
    Tool(
        name="RollDice",
        func=dice_roll,
        description="call this to get the result of rolling dice.",
    )
]


class Enemy:
    def __init__(self, name, stats, identifier):
        # Get the prompt to use - you can modify this!
        prompt = hub.pull("hwchase17/openai-tools-agent")
        self.messages = []
        prompt.messages[0].prompt.template = create_enemy_prompt(
            name, stats, identifier
        )

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        agent = create_openai_tools_agent(llm, tools, prompt)
        self.executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )

    def talk(self, message):
        response = self.executor.invoke(
            {
                "input": message,
                "chat_history": self.messages,
            }
        )
        self.messages += [
            HumanMessage(content=message),
            AIMessage(content=response["output"]),
        ]
        return response
