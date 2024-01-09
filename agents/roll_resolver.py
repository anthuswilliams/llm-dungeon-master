import random
import re
from typing import List

from langchain.agents import AgentExecutor, Tool
from langchain.agents import create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.chat_models import ChatOpenAI

import sys
sys.path.append(".")
import retrievers.character_sheet as chardb

def dice_roll(query: str) -> List[int]:
    results = re.search(r"^(\d+)d(\d+)$", query)
    if not results:
        raise ValueError(f"query {query} is uninterpretable")

    num = results.group(1)
    val = results.group(2)

    return [random.randint(1, int(val)) for i in range(int(num))]
    

tools = [
    create_retriever_tool(
        name="CharacterSheet",        
        retriever=chardb.connect().as_retriever(),
        description="call this to get information from the character sheet"
    ),
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
IMPORTANT!!! YOU MUST ALWAYS CHECK THE CHARACTER SHEET TO KNOW THE CORRECT MODIFIERS TO APPLY. 

Return the result and an explanation of why you got the result that you did.
Examples:
"You rolled a 3 and a 5. Because you have disadvantage, you take the lower roll. With your +2 modifier, your result is 5."
"You rolled an 8 and a 17. Because you have advantage, you take the higher roll. With your +1 modifier, your result is 18."
"You rolled a 4. Because you have a +4 modifier listed on your sheet, your result is 8."
"You rolled a 16. Because your modifier is -1, your result is a 15."
"""
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    agent_executor.invoke({
        "input": "Roll an Intimidation check. Roll with disadvantage.",
        "chat_history": [
            # here is my character sheet!
        ]
    })