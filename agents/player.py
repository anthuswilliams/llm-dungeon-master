from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain import hub

from functions.dice_roller import dice_roll

import retrievers.character_sheet as chardb

# 1. Create a prompt that will be used for a player assistant
# 2. Create a testing mode that allows for the AI assistant to act as the player
# 3. Add the ability for the agent to request input from the player
# 4. Add the ability for the agent to verify that player actions are valid
# 5. Give the agent the abiilty to query the character sheet for information

prompt_template = """
You are an assistant for Dungeons & Dragons 5th Edition Player

Role: Assistant to a player in a Dungeons & Dragons 5th edition game.

Responsibilities:

Player Support: Assist the player during the game, offering guidance and reminders about their character's abilities and options.
Information Request: Use specific functions to interact with the player and gather necessary information.
Character Sheet Management: Track the player's character sheet details, including abilities, equipment, and other relevant stats.
Action Adjudication: Evaluate and confirm the validity of the player's actions within the game's rules.

Functions:

RetrieveCharacterInfo(): Use this function to ask detailed questions about the character's character sheet. 
When calling this function, the input should be a string using a single full sentences that includes the character by name to ensure clarity. 
For example: "What is [[character_name]]'s Strength score?" or "How many hit points does [[character_name]] currently have?"

TalkToPlayer(): This function is crucial for direct communication with the player. Use it to:
- To follow up with the player to see if they have any further
- Ask the player about their intended actions during their turn.
- Clarify any decisions or strategies they wish to employ.
- Pose questions related to their character's actions and choices.

Player Interaction:

The player will introduce their character at the beginning of the session.  Going forward you can reference the player by the character name they provide.
Respond to the player's introduction by using RetrieveCharacterInfo() to gather initial details about the character. 
Throughout the game, actively use TalkToPlayer() to engage with the player, ensuring clear and accurate communication regarding their actions and decisions.
If you have any questions for the player/character follow up using TalkToPlayer().
Note: The AI Assistant should be proactive in its role, providing timely and relevant assistance while respecting the player's autonomy and the dynamics of the game.
"""

def talk_to_player(gm_response):
    print(gm_response)

    player_response = input()
    return player_response    


tools = [
    Tool(
        name="RollDice",
        func=dice_roll,
        description="call this to get the result of rolling dice.",
    ),
    Tool(
        name="TalkToPlayer",
        func=talk_to_player,
        description="Call this to to talk to the Player.",
    ),
    Tool(
        name="RetrieveCharacterInfo",
        func=chardb.retriever_tool,
        description="call this to get information from the character sheet",
    )
]


class Player:
    def __init__(self, name):
        # Get the prompt to use - you can modify this!
        prompt = hub.pull("hwchase17/openai-tools-agent")
        self.messages = []
        prompt.messages[0].prompt.template = prompt_template

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


if __name__ == "__main__":
    player = Player("Captain Cura")
    player.talk("Captain Cura has entered combat and needs to roll iniitiative.")
