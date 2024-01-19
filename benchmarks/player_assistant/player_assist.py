import agents.player_assistant as p
import retrievers.character_sheet as chardb
import json
import random 

from langchain.agents import Tool
from langchain.schema import AgentFinish

characters = ["Captain Cura", "Laeni", "Agasan Lateath", "Aros the Unforgiving", "Mendiete Skiari", "Secure", "Gualluwyrm the Awesome", "Aetan 2-H9", "Captain Gielik"]
starting_message = ["A thug has tried to tackle {character_name}.  Please roll a athletics check."]

conversation = []

def test_talk_to_player(gm_response):
    global conversation
    conversation.append(f"Assitant (to player): {gm_response}")
    player_response = "I rolled a 15.  Please add my modifiers."
    conversation.append(f"Player: {player_response}")
    return player_response    

def test_talk_to_DM(assistant_message):
    global conversation
    conversation.append(f"Assistant (to DM): {assistant_message}") 
    return AgentFinish(return_values={"output": assistant_message}, log=assistant_message)

def capture_retrieve_character_info(assistant_request):
    global conversation
    conversation.append(f"Assistant (to librarian): {assistant_request}")
    librarian_response = chardb.retriever_tool(assistant_request)
    conversation.append(f"Librarian: {librarian_response}")
    return librarian_response

tools = [
    Tool(
        name="TalkToPlayer",
        func=test_talk_to_player,
        description="Call this to to talk to the Player.",
    ),
    Tool(
        name="RetrieveCharacterInfo",
        func=capture_retrieve_character_info,
        description="call this to get information from the character sheet",
    ),
    Tool(
        name="TalkToDM",
        func=test_talk_to_DM,
        description="call this to talk to the AI DM",
    ),
]


all_conversations = {}

for character in characters:
    player_assistant = p.PlayerAssitant(injected_tools=tools)
    dm_request = starting_message[0].format(character_name=character)
    conversation.append(f"DM: {dm_request}")
    response = player_assistant.talk(dm_request)
    all_conversations[character] = "/n/n".join(conversation)
    conversation = []

random_identifier = str(random.randint(0, 1000000))
with open(f"benchmarks/player_assistant/unscored/conversations_{random_identifier}.json", "w") as fh:
    fh.write(json.dumps(all_conversations, indent=4))
    