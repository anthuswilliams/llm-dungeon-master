from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain import hub
from langchain.pydantic_v1 import BaseModel, Field

import random

chat = ChatOpenAI()

system_prompt = """
You are an experienced dungeon master for Dungeons & Dragons 5th edition. We are going to play a short encounter.
You will be in charge of generating the encounter and keeping track of the order in which they take their turns.

There will be one player fighting two goblins (Goblin A and Goblin B) in this encounter.
You will ask what each participants name and their Initiative and wait for their response. The
player with the highest initiative will go first.

After you get each inititive, you will ask each participant and the goblins what they would like to do on their turn.
"""


def create_goblin_prompt(name):
    goblin_stats = f"""\n
        "initiative": {random.randint(1, 20)+10},
        "armor_class": 15,
        "hit_points": 7,
    """

    prompt = f"""You are a goblin in a game of Dungeons & Dragons 5th edition. Your name is {name}. 
        You are in a dungeon and you are about to fight a party of adventurers. Here is your stats: {goblin_stats}"""

    return prompt


def talk_to_goblin_a(gm_response):
    goblin_prompt = create_goblin_prompt("Goblin A")
    goblin_messages = [
        SystemMessage(content=goblin_prompt),
        HumanMessage(content=gm_response),
    ]

    goblin_response = chat.invoke(goblin_messages)
    return goblin_response


def talk_to_goblin_b(gm_response):
    goblin_prompt = create_goblin_prompt("Goblin B")
    goblin_messages = [
        SystemMessage(content=goblin_prompt),
        HumanMessage(content=gm_response),
    ]

    goblin_response = chat.invoke(goblin_messages)
    return goblin_response


def talk_to_player(gm_response):
    print(gm_response)

    player_response = input()
    return player_response


class TalkToGoblin(BaseModel):
    query: str = Field(
        description="Query to talk to the goblins.  The query should be full sentences."
    )


tools = [
    Tool(
        name="Chat_with_Goblin_A",
        func=talk_to_goblin_a,
        args_schema=TalkToGoblin,
        description="Call this to to talk to Goblin A.",
    ),
    Tool(
        name="Chat_with_Goblin_B",
        func=talk_to_goblin_b,
        args_schema=TalkToGoblin,
        description="Call this to to talk to Goblin B.",
    ),
    Tool(
        name="Chat_with_Player",
        func=talk_to_player,
        description="Call this to to talk to the player or Captain Cura.",
    ),
]

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages[0].prompt.template = system_prompt

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    agent_executor.invoke(
        {
            "input": "Start the encounter. The player's character is Captain Cura and their inititative is 15.",
            "chat_history": [
                # here is my character sheet!
            ],
        }
    )
