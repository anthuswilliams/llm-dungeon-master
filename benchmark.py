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

SEEDED_ROLL = {}

def seed_dice_roll():
    global SEEDED_ROLL
    SEEDED_ROLL = {"20": [random.randint(1, 20), random.randint(1, 20)]}


def dice_roll(query: str) -> List[int]:
    results = re.search(r"^(\d+)d(\d+)$", query)
    if not results:
        raise ValueError(f"query {query} is uninterpretable")

    num = results.group(1)
    val = results.group(2)

    if int(num) == 1:
        return SEEDED_ROLL[val][0:-1]
    else:
        return SEEDED_ROLL[val]

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
    )
]

def get_modifier_from_sheet(sheet, skill):
    # assuing skill is Athletics and sheet is 05_fast
    return 5

def random_skill():
    return "Roll an Athletics check."

def select_random_sheet():
    with open("agents/05_fast.txt", "r") as fh:
        sheet = fh.read()
    return sheet

def benchmark(prompt):
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    for i in range(10):
        seed_dice_roll()
        sheet = select_random_sheet()
        skill = random_skill()
        # randomly apply advantage or disadvantage
    
        expected_result = SEEDED_ROLL["20"][0] + get_modifier_from_sheet(sheet, skill)
       
        rslt = agent_executor.invoke({
            "input": f"Roll a {skill} check.",
            "chat_history": []
        })
    
        # evaluate_and_score(rslt)
        print(rslt, expected_result)

if __name__ == "__main__":
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

    benchmark(prompt)