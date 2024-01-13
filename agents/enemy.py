from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain import hub
from langchain.pydantic_v1 import BaseModel, Field
# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
  

import random
from typing import List
import re

prompt_template = """
You are a goblin in a game of Dungeons & Dragons 5th edition. Your name is {name}.
Here is your character sheet: {stats}

When you are asked to make a roll, you (a) roll the dice using the RollDice() function,
and then (b) apply any modifiers as indicated by your character sheet.
IMPORTANT!!! YOU MUST ALWAYS CHECK THE CHARACTER SHEET TO KNOW THE CORRECT MODIFIERS TO APPLY.

Example:
I rolled a 4. I have {initiative_modifier} on initiative, so my initiative is 6
"""

def create_goblin_prompt(name):
    initiative_modifier = "+2"
    goblin_stats = f"""\n
        "initiative_modifier": {initiative_modifier},
        "armor_class": 15,
        "hit_points": 7,
    """

    prompt = prompt_template.format(name=name, stats=goblin_stats, initiative_modifier=initiative_modifier)
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

class Goblin:
    def __init__(self, name):
        self.messages = []
        prompt.messages[0].prompt.template = create_goblin_prompt(name)

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        agent = create_openai_tools_agent(llm, tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        
    def talk(self, message):
        response = self.executor.invoke(
            {
                "input": message,
                "chat_history": self.messages,
            }
        )
        self.messages += [HumanMessage(content=message), AIMessage(content=response["output"])]
        return response