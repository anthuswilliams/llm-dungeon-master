from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain import hub
from langchain.pydantic_v1 import BaseModel, Field

import random

chat = ChatOpenAI()

system_prompt = """
You are an experienced dungeon-master for Dungeons & Dragons 5th edition. You are administering an encounter
between a player and enemies.
Participants: 1 Human Player, 2 AI-Controlled Goblins ("Grothnar" and "Halbirk")
Functions:
TalkToPlayer(): Function to communicate with the human player.
TalkToGoblin(): Function to communicate with the AI-controlled goblins. You must specify which Goblin you are talking to and what you want to ask, for example "Halbirk, what do you want to do?"
Procedure:
Initiative Roll: The AI DM begins by using TalkToPlayer() and TalkToGoblin() to ask each participant for their Initiative.
Collecting Initiative Results: The AI DM receives and records the Initiative from each participant.
Determining Initiative Order: The AI DM arranges the participants in descending order of their Initiative, from highest to lowest.
Commencing Combat:
You start the combat round with the participant who rolled the highest initiative.
Uses TalkToPlayer() to engage with the human player and TalkToGoblin() to manage the AI goblins' actions.
Ensures that each participant takes their turn according to the initiative order. Continue cycling through the initiative order until the combat has ended.
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


goblin_messages = {
    "Grothnar": [
        SystemMessage(content=create_goblin_prompt("Grothnar")),
    ],
    "Halbirk": [
        SystemMessage(content=create_goblin_prompt("Halbirk")),
    ]
}

def talk_to_goblin(message):
    global goblin_messages
    identifier = "Grothnar" if "Grothnar" in message else "Halbirk"
    goblin_messages[identifier] = goblin_messages[identifier] + [
        HumanMessage(content=message),
    ]

    goblin_response = chat.invoke(goblin_messages[identifier])
    return goblin_response

def talk_to_player(gm_response):
    print(gm_response)

    player_response = input()
    return player_response

class TalkToGoblin(BaseModel):
    identifier: str = Field('Which goblin you want to talk to, for example "A"')
    query: str = Field("The question you wish to ask the goblin")
    
tools = [
    Tool(
        name="TalkToGoblin",
        func=talk_to_goblin,
        description="Call this to to talk to one of the goblins.",
    ),
    Tool(
        name="TalkToPlayer",
        func=talk_to_player,
        description="Call this to to talk to the player.",
    ),
]

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")
prompt.messages[0].prompt.template = system_prompt

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# llm_with_tools = llm.bind(
#     functions=[
#         convert_pydantic_to_openai_function(TalkToGoblin),
#     ]
# )

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

if __name__ == "__main__":
    agent_executor.invoke(
        {
            "input": "Start the encounter.",
            "chat_history": [
                # here is my character sheet!
            ],
        }
    )
