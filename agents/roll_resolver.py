import random
import re
from typing import List

from langchain.agents import AgentExecutor, Tool
from langchain.agents import create_openai_tools_agent
from langchain.chat_models import ChatOpenAI


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
    ),
]

from langchain import hub

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages[0].prompt.template = """
You are an experienced player of Dungeons & Dragons 5th edition. When you are asked to roll a skill check,
you (a) roll the dice and then (b) apply any modifiers as indicated by your character sheet.
Return the result and an explanation of why you got the result that you did.
Examples:
"You rolled a 3 and a 5. Because you have disadvantage, your result is 3."
"You rolled an 8 and a 17. Because you have advantage, your result is 17."
"""
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({
    "input": "Roll a Perception check. You have advantage due to the clear day",
    "chat_history": [
        # here is my character sheet!
    ]
})